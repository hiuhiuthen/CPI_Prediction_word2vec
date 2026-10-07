"""PhoW2V vocabulary expansion, exact keys only. No training or vector averaging.
Run --help for arguments. Requires gensim, uses existing installed version.
"""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import unicodedata

TONES = dict(zip(
    ['òa','óa','ỏa','õa','ọa','òe','óe','ỏe','õe','ọe','ùy','úy','ủy','ũy','ụy'],
    ['oà','oá','oả','oã','oạ','oè','oé','oẻ','oẽ','oẹ','uỳ','uý','uỷ','uỹ','uỵ']))

def normalize(s):
    s = unicodedata.normalize('NFC', s).replace('_', ' ').lower()
    for a, b in TONES.items():
        s = s.replace(a, b)
    return ' '.join(s.split())

def clean(s):
    return s.replace('_', ' ').strip(' \t\r\n.,;:!?\"\'()[]{}')

def collect(node, group=()):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from collect(value, group + (key,))
    elif isinstance(node, list):
        for value in node:
            if not isinstance(value, str) or not value.strip():
                raise ValueError('Danh sach tu khoa phai chua chuoi khong rong.')
            yield {'seed': value, 'group': list(group)}
    else:
        raise ValueError('Cau truc JSON tu khoa khong hop le.')

def load_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def detect_format(path):
    with path.open('rb') as f:
        header = f.readline(1024).split()
        if len(header) != 2 or not all(x.isdigit() for x in header):
            raise ValueError('Can file vector Word2Vec da giai nen, co header so tu/so chieu.')
        row = f.readline(1024 * 1024)
    try:
        fields = row.decode('utf-8').split()
        if len(fields) != int(header[1]) + 1:
            return True
        for x in fields[1:]:
            float(x)
        return False
    except (UnicodeDecodeError, ValueError):
        return True

def make_lookup(vectors, wanted):
    # Normalized fallback is only for lowercase keys. Case-sensitive vectors
    # such as Va_Ly must not silently substitute for a lowercase common noun.
    # Deliberately capitalized aliases (CPI, USD, VAT) still resolve exactly.
    found = {}
    for key in vectors.index_to_key:
        if key != key.lower():
            continue
        n = normalize(key)
        if n in wanted and n not in found:
            found[n] = key
    return found

def resolve(text, vectors, lookup):
    raw = unicodedata.normalize('NFC', text)
    for key in [raw, raw.replace(' ', '_'), normalize(text).replace(' ', '_')]:
        if key in vectors:
            return key
    return lookup.get(normalize(text))

def reject_reason(token, excluded, stopwords):
    term = clean(token)
    n = normalize(term)
    if n in excluded:
        return 'already_seed_or_query'
    if n in stopwords:
        return 'generic_stopword'
    if not term or not any(c.isalpha() for c in term):
        return 'no_letters'
    if len(term) < 2:
        return 'single_character'
    if any(c in term for c in ['/', '\\', '@', '=', '<', '>', '\ufffd']):
        return 'identifier_url_or_broken_text'
    return None

def review_flags(token):
    parts = clean(token).split()
    flags = []
    if len(parts) >= 2 and sum(p[0].isupper() for p in parts if p) >= 2:
        flags.append('possible_proper_name_or_title_case')
    if any(c.isdigit() for c in token):
        flags.append('contains_digits_check_context')
    return flags

def expand(vectors, seeds, mapping, all_original, topn=20):
    rules = {r['seed']: r for r in mapping['entries']}
    if len(rules) != len(mapping['entries']):
        raise ValueError('Bang anh xa co seed trung.')
    missing_rules = [s['seed'] for s in seeds if s['seed'] not in rules]
    if missing_rules:
        raise ValueError('Bang anh xa thieu seed: ' + '; '.join(missing_rules))
    wanted = {normalize(s['seed']) for s in seeds}
    for r in rules.values():
        for q in r['fallback_queries']:
            wanted.update(normalize(t) for t in q['alternatives'])
    lookup = make_lookup(vectors, wanted)
    excluded = {normalize(clean(t)) for t in all_original} | wanted
    stop = {normalize(t) for t in mapping['candidate_stopwords']}
    cache, results, skipped, unmatched, merged, filtered = {}, [], [], [], {}, []
    methods = Counter()

    def candidates_for(key):
        if key in cache:
            return cache[key]
        kept, seen = [], set()
        # Retrieve more than topn so rejected entries do not occupy output slots.
        limit = min(len(vectors), max(100, topn * 5))
        raw = vectors.most_similar(key, topn=limit)
        while True:
            kept, seen, local_filtered = [], set(), []
            for token, score in raw:
                reason = reject_reason(token, excluded, stop)
                if reason:
                    local_filtered.append({'query_token': key, 'model_token': token,
                                           'similarity': float(score), 'reason': reason})
                    continue
                term = clean(token)
                n = normalize(term)
                if n in seen:
                    continue
                seen.add(n)
                kept.append({'candidate': term, 'model_token': token,
                             'similarity': round(float(score), 6),
                             'status': 'cho_duyet', 'review_flags': review_flags(token)})
                if len(kept) == topn:
                    break
            if len(kept) >= topn or limit >= min(len(vectors), 1000):
                filtered.extend(local_filtered)
                cache[key] = kept
                return kept
            limit = min(len(vectors), 1000, limit * 2)
            raw = vectors.most_similar(key, topn=limit)

    for index, seed in enumerate(seeds, 1):
        rule = rules[seed['seed']]
        key = resolve(seed['seed'], vectors, lookup)
        if key:
            queries = [{'requested_query': seed['seed'], 'model_token': key,
                        'relation': 'original_exact', 'method': 'exact_original'}]
        else:
            queries, seen_keys = [], set()
            for q in rule['fallback_queries']:
                chosen = next(((t, resolve(t, vectors, lookup)) for t in q['alternatives']
                               if resolve(t, vectors, lookup)), None)
                if chosen is None:
                    unmatched.append(dict(seed, alternatives=q['alternatives'], reason='no_exact_key'))
                    continue
                term, key = chosen
                if key not in seen_keys:
                    queries.append({'requested_query': term, 'model_token': key,
                                    'relation': q['relation'], 'method': 'mapped_exact'})
                    seen_keys.add(key)
        if not queries:
            skipped.append(dict(seed, reason='no_exact_original_or_mapped_key', note=rule['note']))
            print(f'[{index}/{len(seeds)}] BO QUA: {seed["seed"]}', flush=True)
            continue
        query_records = []
        for q in queries:
            methods[q['method']] += 1
            candidates = candidates_for(q['model_token'])
            query_records.append(dict(q, candidates=candidates))
            for c in candidates:
                entry = merged.setdefault(normalize(c['candidate']),
                    {'candidate': c['candidate'], 'status': 'cho_duyet',
                     'review_flags': c['review_flags'], 'matches': []})
                entry['matches'].append(dict(seed, query=q['requested_query'],
                    query_token=q['model_token'], relation=q['relation'], similarity=c['similarity']))
        results.append(dict(seed, mapping_note=rule['note'], queries=query_records))
        print(f'[{index}/{len(seeds)}] {seed["seed"]}: {len(queries)} truy van nguyen cum', flush=True)
    return {'summary': {'total_seeds': len(seeds), 'queried_seeds': len(results),
                        'skipped_seeds': len(skipped), 'unmatched_fallback_queries': len(unmatched),
                        'unique_queries_executed': len(cache), 'query_methods': dict(methods),
                        'candidate_links': sum(len(e['matches']) for e in merged.values()),
                        'unique_candidates': len(merged), 'filtered_hits_unique_queries': len(filtered)},
            'by_seed': results, 'unique_candidates': sorted(merged.values(), key=lambda x:x['candidate']),
            'skipped_seeds': skipped, 'unmatched_queries': unmatched, 'filtered_candidates': filtered}

def main():
    here = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True, type=Path)
    p.add_argument('--json', type=Path, default=here/'vocab.json')
    p.add_argument('--mapping', type=Path, default=here/'anh_xa_truy_van.json')
    p.add_argument('--topn', type=int, default=20)
    p.add_argument('--output', type=Path, default=here/'res.json')
    p.add_argument('--format', choices=['auto','text','binary'], default='auto')
    args = p.parse_args()
    if not 1 <= args.topn <= 200:
        p.error('--topn can nam trong khoang 1..200')
    for path in [args.model, args.json, args.mapping]:
        if not path.is_file():
            p.error(f'Khong tim thay: {path}')
    if args.output.resolve() in {x.resolve() for x in [args.model,args.json,args.mapping]}:
        p.error('File ket qua khong duoc ghi de file dau vao.')
    original, mapping = load_json(args.json), load_json(args.mapping)
    roots = ['nhom_1_cpi','nhom_2_tac_nhan']
    seeds = list(collect({k:original[k] for k in roots}))
    from gensim.models import KeyedVectors
    binary = detect_format(args.model) if args.format == 'auto' else args.format == 'binary'
    print('Dang nap PhoW2V...', flush=True)
    vectors = KeyedVectors.load_word2vec_format(str(args.model), binary=binary)
    print(f'Da nap {len(vectors):,} vector, {vectors.vector_size} chieu. Dang doi chieu truy van...', flush=True)
    result = expand(vectors, seeds, mapping, [x['seed'] for x in collect(original)], args.topn)
    result['metadata'] = {'script_version':'2.1', 'task':'candidate_expansion_no_training',
        'model_file':args.model.name, 'vector_size':vectors.vector_size,
        'model_vocabulary_size':len(vectors), 'topn_per_query':args.topn,
        'groups':roots, 'mean_vectors_used':False, 'automatic_segmentation_used':False,
        'query_case_policy':'exact_requested_case_or_lowercase_normalized_key_only',
        'score':'cosine_similarity_not_probability', 'mapping_author':'assistant_curated',
        'mapping_sha256':hashlib.sha256(args.mapping.read_bytes()).hexdigest(),
        'seed_file_sha256':hashlib.sha256(args.json.read_bytes()).hexdigest(),
        'gensim_version':importlib.metadata.version('gensim'),
        'note':'All candidates need review. Mapped queries may broaden a seed; relation records this.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('XONG:',args.output.resolve())
    print(json.dumps(result['summary'],ensure_ascii=False,indent=2))

if __name__ == '__main__':
    try:
        main()
    except MemoryError:
        sys.exit('Khong du RAM de nap model. Dong bot ung dung va dung ban words_100dims.')
    except (ValueError, OSError, KeyError) as e:
        sys.exit('LOI: '+str(e))
