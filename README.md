# Xây dựng và mở rộng bộ từ vựng CPI bằng PhoW2V

Dự án xây dựng bộ từ khóa tiếng Việt để hỗ trợ tìm kiếm, thu thập và sàng lọc các bài báo liên quan đến chỉ số giá tiêu dùng (CPI). Quy trình gồm ba bước: trích xuất từ gốc từ 7 thông cáo tình hình giá của cơ quan thống kê Việt Nam; mở rộng bằng PhoW2V; rà soát và tổng hợp bộ từ cuối cùng.

**Kết quả đã thực hiện:** 188 từ/cụm từ gốc + 793 từ/cụm từ mở rộng được giữ lại = **981 mục từ**. Bộ cuối cùng có 3 nhóm: 11 nhóm hàng hóa/dịch vụ CPI, tác nhân vĩ mô, và từ chỉ tăng/giảm.

## 1. Các file trong dự án

| File | Vai trò |
| --- | --- |
| `extended_vocab.py` | Chương trình mở rộng từ vựng|
| `vocab.json` | 188 từ/cụm từ gốc ở bước 1; là đầu vào của chương trình. |
| `anh_xa_truy_van.json` | Cấu hình truy vấn thay thế khi mô hình không có nguyên cụm từ gốc; gồm 167 quy tắc và danh sách từ dừng. |
| `res.json` | Kết quả chạy bước 2 đã có: 1.832 ứng viên duy nhất, kèm điểm, truy vấn, từ gốc và thông tin để đối chiếu. |
| `bo_tu_vung_CPI_hoan_chinh.json` | Bộ từ sau bước 3: 981 mục từ, chỉ giữ cấu trúc nhóm và danh sách từ. |
| `requirements.txt` | Thư viện Python cần để chạy bước 2. |
| `.gitignore` | Loại môi trường Python, vector PhoW2V và file tạm khỏi Git. |
| `README.md` | Nguồn dữ liệu, quy trình, hướng dẫn chạy và giải thích mã nguồn. |

## 2. Bước 1 — Xây dựng bộ từ vựng gốc

### 2.1. Bảy nguồn đầu vào

Bộ từ gốc được tổng hợp từ 7 thông cáo tình hình giá do người nghiên cứu lựa chọn trên website NSO (nguồn Tổng cục Thống kê/Cục Thống kê). Danh sách nguồn của bước này gồm:

1. [Tháng Ba và quý I năm 2025](https://www.nso.gov.vn/du-lieu-va-so-lieu-thong-ke/2025/04/thong-cao-bao-chi-ve-tinh-hinh-gia-thang-ba-va-quy-i-nam-2025/)
2. [Tháng Sáu, quý II và 6 tháng đầu năm 2025](https://www.nso.gov.vn/tin-tuc-thong-ke/2025/07/thong-cao-bao-chi-ve-tinh-hinh-gia-thang-sau-quy-ii-va-6-thang-dau-nam-2025/)
3. [Tháng Chín, quý III và 9 tháng năm 2025](https://www.nso.gov.vn/du-lieu-va-so-lieu-thong-ke/2025/10/thong-cao-bao-chi-ve-tinh-hinh-gia-thang-chin-quy-iii-va-9-thang-nam-2025/)
4. [Tháng Mười Hai, quý IV và năm 2025](https://www.nso.gov.vn/du-lieu-va-so-lieu-thong-ke/2026/01/thong-cao-bao-chi-ve-tinh-hinh-gia-thang-muoi-hai-quy-iv-va-nam-2025/)
5. [Tháng Ba và quý I năm 2026](https://www.nso.gov.vn/du-lieu-va-so-lieu-thong-ke/2026/04/thong-cao-bao-chi-ve-tinh-hinh-gia-thang-ba-va-quy-i-nam-2026/)
6. [Tháng Sáu, quý II và 6 tháng đầu năm 2026](https://www.nso.gov.vn/tin-tuc-thong-ke/2026/07/thong-cao-bao-chi-ve-tinh-hinh-gia-thang-sau-quy-ii-va-6-thang-dau-nam-2026/)
7. [Tháng Chín, quý III và 9 tháng năm 2026](https://www.nso.gov.vn/tin-tuc-thong-ke/2026/10/thong-cao-bao-chi-ve-tinh-hinh-gia-thang-chin-quy-iii-va-9-thang-nam-2026/)

### 2.2. Cách thực hiện

Người nghiên cứu cung cấp 7 nguồn và yêu cầu AI hỗ trợ đọc, trích xuất các từ/cụm từ về hàng hóa, dịch vụ, tác nhân kinh tế và biến động giá. Phạm vi trích xuất của bước 1 được giới hạn trong 7 nguồn này; không tự bổ sung từ ngoài nguồn vào bộ từ gốc. Các mục được tổng hợp, loại trùng và phân vào ba nhóm, rồi lưu thành JSON UTF-8 để chương trình đọc được.

Đây là bước lựa chọn từ có AI hỗ trợ và có quyết định của người nghiên cứu. `extended_vocab.py` không thực hiện đọc website hoặc trích xuất từ ở bước này. File gọn `vocab.json` không chứa cột nguồn đối chiếu vì muốn tinh gọn nhất có thể để đưa vào mô hình tiếp theo.

### 2.3. Ba nhóm từ vựng
Sau khi tham khảo từ GVHD, nhóm quyết định tạo bộ từ vựng và chia làm 3 nhóm:
**Nhóm 1 — 11 nhóm cấu thành CPI:**
11 nhóm này đã được kế thừa theo tổng cục thống kê và các nghiên cứu về CPI khác
1. Hàng ăn và dịch vụ ăn uống.
2. Đồ uống và thuốc lá.
3. May mặc, mũ nón, giày dép.
4. Nhà ở, điện nước, chất đốt và vật liệu xây dựng.
5. Thiết bị và đồ dùng gia đình.
6. Thuốc và dịch vụ y tế.
7. Giao thông.
8. Bưu chính viễn thông và thông tin truyền thông.
9. Giáo dục.
10. Văn hóa, giải trí và du lịch.
11. Hàng hóa và dịch vụ khác.

**Nhóm 2 — Tác nhân vĩ mô:** tỷ giá, lãi suất, chính sách, năng lượng, chi phí, cung cầu, chuỗi cung ứng, thiên tai/dịch bệnh và các từ nhận diện CPI/lạm phát. Trong bộ gốc, các từ được chia thành các nhánh để tổ chức dữ liệu; trong bộ cuối, chúng được làm phẳng thành một danh sách chung, không gắn riêng với một nhóm CPI.

**Nhóm 3 — Biến động:** các từ/cụm từ chỉ tăng hoặc giảm. Nhóm này có 21 mục, gồm 12 mục tăng và 9 mục giảm.

Đầu ra bước 1 có **188 mục từ**, trong đó **167 mục thuộc nhóm 1 và 2** được đưa vào bước mở rộng. Cách tổ chức nhóm phục vụ dự án; không xem các từ mở rộng sau này là một danh mục phân loại chính thức do NSO công bố.

## 3. Bước 2 — Mở rộng từ vựng bằng PhoW2V

### 3.1. Mô hình được sử dụng

Dự án sử dụng **PhoW2V_words_100dims** của VinAI: bộ vector Word2Vec tiếng Việt đã được huấn luyện sẵn ở cấp độ từ, mỗi vector có 100 chiều. Theo README của PhoW2V, các bộ vector được huấn luyện trên kho văn bản tiếng Việt dung lượng 20 GB.

- [Kho mã nguồn và hướng dẫn PhoW2V](https://github.com/VinAIResearch/PhoW2V)
- [Thư mục tải](https://drive.google.com/drive/folders/1NZhZFYbcwKzLpvvGdJUdPbwEVdVW4E3j?usp=drive_link)
- [Bài báo được PhoW2V yêu cầu trích dẫn](https://aclanthology.org/2020.findings-emnlp.364/)

File sử dụng sau giải nén là `word2vec_vi_words_100dims.txt`, khoảng 1,9 GB. Kết quả đã chạy ghi nhận **1.587.507 vector, mỗi vector 100 chiều**.

JSON từ vựng đóng vai trò danh sách truy vấn. Chương trình nạp vector bằng `gensim.models.KeyedVectors.load_word2vec_format()` rồi tìm các vector gần nhau. Không có bước huấn luyện mới, fine-tuning hoặc thay đổi trọng số của PhoW2V trong quy trình này.

Ở phiên bản word, một từ ghép thường được lưu thành khóa có dấu gạch dưới, ví dụ `thực_phẩm`. Con số 100 là số thành phần của vector, không phải số từ được trả về.

### 3.2. Luồng xử lý

1. Đọc `vocab.json` và lấy 167 từ gốc (*seed*) thuộc `nhom_1_cpi` và `nhom_2_tac_nhan`; giữ thông tin nhóm của từng seed.
2. Đọc `anh_xa_truy_van.json` và kiểm tra các seed đều có quy tắc ánh xạ.
3. Nạp PhoW2V; tạo bảng tra những khóa viết thường khớp sau chuẩn hóa Unicode, khoảng trắng và vị trí dấu thanh.
4. Ưu tiên tìm nguyên từ/cụm từ gốc trong mô hình. Nếu tìm được, truy vấn trực tiếp từ đó và không dùng fallback.
5. Nếu không có nguyên cụm, lần lượt thử các phương án thay thế được khai báo trong bảng ánh xạ. Mỗi nhóm `alternatives` chọn phương án đầu tiên tồn tại. Một seed có thể sinh nhiều truy vấn khác nhau.
6. Nếu không tìm được từ gốc hay phương án thay thế nào, ghi seed vào `skipped_seeds`; không tự tạo vector mới.
7. Với mỗi khóa truy vấn, tìm các hàng xóm bằng `most_similar()`, lọc sơ bộ và lấy tối đa 20 ứng viên hợp lệ khi `--topn 20`.
8. Gom các ứng viên trùng nhau theo dạng chuẩn hóa, giữ toàn bộ quan hệ với seed/truy vấn trong `matches`, rồi xuất `res.json` để duyệt.

Ví dụ có trong bảng ánh xạ: seed **“giá gạo”** được tra nguyên cụm trước. Nếu không có khóa phù hợp, chương trình thử **“gạo”** với quan hệ `commodity_head`. Việc bỏ phần “giá” giúp tìm từ liên quan đến mặt hàng nhưng làm rộng phạm vi: bài báo có nhắc gạo chưa chắc nói về biến động giá gạo.

Các phương án ánh xạ do công cụ AI hỗ trợ xây dựng là cấu hình ở **bước 2**, không được coi là từ đã trích nguyên văn từ 7 thông cáo ở bước 1. Chương trình cũng loại các từ gốc và các dạng truy vấn dự kiến khỏi danh sách ứng viên mở rộng để tránh đưa lại chúng như từ mới.

### 3.3. Tương đồng vector và lọc sơ bộ

Độ tương đồng cosine đo mức gần nhau về hướng giữa hai vector:

```text
cosine(u, v) = (u · v) / (||u|| × ||v||)
```

Điểm cao cho biết hai từ gần nhau trong không gian biểu diễn đã học. Chúng có thể cùng chủ đề, thường xuất hiện trong ngữ cảnh tương tự, hoặc có quan hệ khác; không nhất thiết đồng nghĩa. Điểm này không phải xác suất một từ hay một bài báo liên quan đến CPI.

Chương trình không áp dụng ngưỡng cosine tối thiểu. Tham số `--topn` giới hạn số ứng viên sau lọc trên **mỗi truy vấn**, không phải trên mỗi seed hay toàn bộ dự án. Hàm tìm ứng viên lấy trước tối đa `max(100, topn × 5)` hàng xóm, giới hạn bởi kích thước mô hình; nếu chưa đủ thì mở rộng số lấy về, với trần 1.000 ở các lần mở rộng.

Bộ lọc sơ bộ loại các trường hợp: đã là seed/truy vấn, thuộc danh sách từ dừng, không có chữ cái, quá ngắn, hoặc chứa một số ký tự URL/mã/văn bản hỏng. Tên riêng nghi vấn và từ có chữ số chỉ được **gắn cờ cần xem xét**, chưa tự động loại.

### 3.4. Kết quả lần chạy đã lưu

| Chỉ tiêu | Giá trị |
| --- | ---: |
| Seed thuộc nhóm 1 và 2 | 167 |
| Seed có ít nhất một truy vấn thành công | 104 |
| Seed bị bỏ qua vì không có khóa phù hợp | 63 |
| Nhóm phương án fallback không tìm được khóa | 34 |
| Khóa truy vấn duy nhất thực sự thực hiện | 108 |
| Bản ghi truy vấn nguyên cụm gốc | 32 |
| Bản ghi truy vấn qua ánh xạ | 88 |
| Liên kết seed–truy vấn–ứng viên | 2.400 |
| Ứng viên duy nhất sau gom trùng | 1.832 |
| Lượt ứng viên bị bộ lọc sơ bộ loại trên các truy vấn duy nhất | 654 |


### 3.5. Cấu trúc kết quả `res.json`

| Trường | Ý nghĩa |
| --- | --- |
| `summary` | Số lượng seed, truy vấn, ứng viên và các thống kê khác. |
| `by_seed` | Kết quả theo từng từ gốc, nhóm, ghi chú ánh xạ và các truy vấn đã dùng. |
| `unique_candidates` | Danh sách ứng viên đã gom trùng, cùng `matches` để truy ngược về seed. |
| `skipped_seeds` | Seed không có truy vấn sử dụng được. |
| `unmatched_queries` | Các nhóm phương án thay thế không tìm được khóa. |
| `filtered_candidates` | Những lượt ứng viên bị loại tự động và lý do loại. |
| `metadata` | Phiên bản thuật toán, số chiều, số vector, phiên bản Gensim, SHA-256 của đầu vào và cấu hình chạy. |

Các trường thường gặp: `seed` là từ gốc; `requested_query` là nội dung được yêu cầu tra; `model_token` là khóa thực tế trong PhoW2V; `candidate` là từ đề xuất đã làm sạch để đọc; `similarity` là cosine; `review_flags` là cờ rà soát. `status: "cho_duyet"` trong `res.json` thể hiện đây là kết quả trước bước duyệt.

## 4. Giải thích từng hàm trong `extended_vocab.py`

Đây là file Python thực thi duy nhất trong gói. Các file JSON là dữ liệu/cấu hình, không chứa hàm Python.

| Hàm/thành phần | Đầu vào và kết quả | Vai trò chi tiết |
| --- | --- | --- |
| `TONES` | Bảng thay thế vị trí dấu thanh | Ánh xạ một số cách đặt dấu như `òa` → `oà`; được dùng khi so khớp, không viết lại file từ gốc. |
| `normalize(s)` | Chuỗi → chuỗi chuẩn hóa | Chuẩn hóa Unicode NFC, thay `_` bằng khoảng trắng, chuyển chữ thường, chuẩn hóa dấu theo `TONES` và gom khoảng trắng. Dùng để tra cứu và nhận diện trùng. |
| `clean(s)` | Token → chuỗi dễ đọc | Thay `_` bằng khoảng trắng, bỏ khoảng trắng và một số dấu câu ở hai đầu. Không tự sửa chính tả hay loại dấu câu ở giữa. |
| `collect(node, group=())` | JSON lồng nhau → luồng bản ghi `seed`, `group` | Duyệt đệ quy qua dictionary và list, ghi lại đường dẫn nhóm. Từ chối phần tử không phải chuỗi, chuỗi rỗng hoặc cấu trúc không hỗ trợ. |
| `load_json(path)` | Đường dẫn → đối tượng Python | Đọc JSON bằng `utf-8-sig`, chấp nhận file UTF-8 có hoặc không có BOM. |
| `detect_format(path)` | File vector → boolean | Kiểm tra header gồm số từ và số chiều, thử đọc hàng vector đầu tiên. Trả `False` cho định dạng text và `True` khi suy đoán binary. Có thể chỉ định `--format text` để không dùng suy đoán. |
| `make_lookup(vectors, wanted)` | Mô hình + tập dạng cần tra → dictionary | Duyệt từ vựng mô hình, chỉ lấy khóa viết thường. Với mỗi dạng chuẩn hóa cần tra, giữ khóa đầu tiên tìm được; tránh tự thay từ thường bằng khóa viết hoa qua lookup dự phòng. |
| `resolve(text, vectors, lookup)` | Chuỗi truy vấn → khóa mô hình hoặc `None` | Thử lần lượt chuỗi NFC nguyên dạng, dạng nối khoảng trắng bằng `_`, dạng chuẩn hóa có `_`; nếu đều không có thì dùng lookup dự phòng. |
| `reject_reason(token, excluded, stopwords)` | Token + tập loại → lý do hoặc `None` | Kiểm tra trùng seed/truy vấn, từ dừng, không có chữ, một ký tự và một số dấu hiệu mã/URL/văn bản hỏng. `None` nghĩa là qua bộ lọc sơ bộ. |
| `review_flags(token)` | Token → danh sách cờ | Gắn cờ khi có ít nhất hai thành phần bắt đầu bằng chữ hoa, hoặc có chữ số. Đây là heuristic để duyệt, không phải mô hình nhận diện thực thể. |
| `expand(vectors, seeds, mapping, all_original, topn=20)` | Mô hình + đầu vào → dictionary kết quả | Kiểm tra quy tắc ánh xạ, tạo lookup và tập loại, chọn truy vấn cho từng seed, tìm ứng viên, gom kết quả, giữ liên kết đối chiếu và tính thống kê. |
| `candidates_for(key)` — hàm lồng trong `expand` | Khóa mô hình → danh sách ứng viên | Dùng cache để tái sử dụng kết quả; gọi `most_similar`, lấy dư hàng xóm, lọc sơ bộ, bỏ trùng chuẩn hóa, gắn cờ và lấy tối đa `topn` ứng viên. |
| `main()` | Tham số dòng lệnh → file JSON đầu ra | Đọc tham số, kiểm tra file và `topn`, ngăn ghi đè đầu vào, đọc seed/mapping, nạp Gensim, gọi `expand`, thêm metadata và ghi UTF-8 JSON. |
| Khối `if __name__ == '__main__'` | Điểm vào khi chạy script | Gọi `main`; đổi lỗi thiếu RAM và một số lỗi dữ liệu/đường dẫn thành thông báo dễ đọc rồi kết thúc chương trình. |

Bảng ánh xạ gồm `entries` và `candidate_stopwords`. Mỗi entry có `seed`, `group`, `try_original_first`, `fallback_queries`, `note`; mỗi fallback có `alternatives` và `relation`. Trong mã hiện tại, chương trình luôn thử seed trước; trường `try_original_first` mô tả cấu hình chứ không điều khiển một nhánh riêng. Nhóm của kết quả lấy từ `vocab.json`; `group` trong mapping phục vụ mô tả. Các trường tác giả/trạng thái trong mapping là metadata lúc soạn, không phải kết quả đánh giá mô hình.

## 5. Cách chạy trên Windows bằng VS Code

### 5.1. Chuẩn bị

Mở thư mục dự án bằng **File → Open Folder**, sau đó mở **Terminal → New Terminal**. Các lệnh bên dưới chạy tại thư mục chứa `extended_vocab.py`.

Tải bản **words 100dims** từ nguồn PhoW2V ở trên, giải nén để có đường dẫn:

```text
word2vec_vi_words_100dims/word2vec_vi_words_100dims.txt
```

Không nạp trực tiếp ZIP. Nếu đã có `.venv` và đã chạy mô hình thành công, có thể sử dụng môi trường đó. Để tạo môi trường mới với Python 3.13 đã cài:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` dùng Gensim 4.4.0, đúng phiên bản được ghi trong kết quả đã chạy. NumPy và SciPy được cài theo phụ thuộc của Gensim. Script hiện tại không dùng Underthesea; không cần gỡ Underthesea nếu môi trường cũ đã có. File requirements không khóa toàn bộ phụ thuộc gián tiếp nên không bảo đảm môi trường nhị phân giống tuyệt đối lần chạy trước.

## 6. Bước 3 — Rà soát, quyết định và tổng hợp

### 6.1. Rà soát ứng viên

Sau khi có `res.json`, AI hỗ trợ đọc các ứng viên và đề xuất phân loại thành: các từ bị loại, từ cần xem xét và các nhóm biến thể cách viết để trực tiếp quyết định.

Các tiêu chí gồm: mức liên quan đến hàng hóa/dịch vụ CPI hoặc tác nhân vĩ mô; tên người/địa danh/thương hiệu và sự phù hợp với mục tiêu lọc bài; từ quá chung, mảnh văn bản hoặc mã khó hiểu; lỗi chính tả; biến thể cách viết. Những trường hợp chưa rõ được đưa ra xem xét thay vì tự sửa hoặc tự thêm từ mới.

Kết quả rà soát ban đầu được chia thành bốn phần không chồng lặp:

| Phần | Số mục |
| --- | ---: |
| Đề xuất giữ | 634 |
| Đề xuất loại | 537 |
| Cần xem xét thông thường, ngoài các nhóm biến thể | 463 |
| Ứng viên trong 80 nhóm biến thể cách viết | 198 |
| Tổng cộng | 1.832 |


### 6.2. Quyết định cuối của người nghiên cứu

- Giữ 634 ứng viên được đề xuất giữ ban đầu.
- Không đưa 537 ứng viên đề xuất loại và 463 ứng viên cần xem xét thông thường vào bộ cuối.
- Giữ các biến thể trong 80 nhóm, chỉ loại 39 cách viết đã được duyệt bỏ; các trường hợp chưa đủ chắc chắn thì giữ lại.
- Không gộp các cách viết được chấp nhận thành một từ duy nhất. Chẳng hạn `giày` và `giầy` được giữ như những cách viết được chấp nhận, không mặc định một dạng là lỗi.
- Không thêm một biến thể mới nếu nó không có trong từ gốc hoặc danh sách ứng viên đã duyệt.

39 mục được duyệt loại khỏi nhóm biến thể:

```text
giuờng, giưởng, gường, diedel, wisky, ruợu, rươu,
martphone, smarphone, smarrtphone, smarthphone, smatphone,
logicstic, logicstics, logictics, logictis, logictisc,
logisctic, logisctis, logisitics, logistisc, logitics,
tuor, cuới, ghạch, dêt, chếbiến, thựcphẩm, lạmphát,
lẫi, qúan, viễn thống, hyrvnia, Heiniken, Heniken,
Hanoitouris, Margareta Wahlstrm, Hermen Borstcho, lítt
```

Do đó, nhóm biến thể còn **198 − 39 = 159 mục**, và tổng số từ mở rộng được chấp nhận là **634 + 159 = 793 mục**. Chính sách giữ các trường hợp biến thể chưa chắc chắn có thể để lại một số tên riêng, thương hiệu hoặc từ cần kiểm chứng ngữ cảnh; không diễn giải bộ cuối là đã loại sạch mọi tên riêng.

### 6.3. Tổng hợp bộ từ cuối

Bộ cuối được tạo bằng cách giữ toàn bộ 188 mục từ gốc, thêm 793 mục được chấp nhận, rồi tổ chức thành ba nhóm. Đối với từ mở rộng, nhóm gắn với seed được dùng làm điểm bắt đầu; một số mục được chuyển nhóm theo nghĩa phù hợp hơn. Quan hệ gần vector với seed không tự chứng minh ứng viên thuộc đúng nhóm CPI đó.

Nhóm tác nhân vĩ mô được làm phẳng thành một danh sách chung. Nhóm tăng/giảm giữ nguyên 21 mục từ gốc và được làm phẳng thành hai danh sách `tang`, `giam`; không được mở rộng bằng PhoW2V trong quy trình này.

Các kiểm tra khi tổng hợp gồm: mọi từ gốc còn nguyên; đủ 793 từ được giữ; không lọt 39 mục đã duyệt loại; không thêm từ ngoài tập gốc và tập chấp nhận; không trùng chuỗi; đủ 3 nhóm lớn và 11 nhánh CPI; JSON đọc được và chỉ chứa các danh sách từ cần dùng.

| Nhóm trong file cuối | Số mục |
| --- | ---: |
| `nhom_1_cpi` — tổng 11 nhóm | 721 |
| `nhom_2_tac_nhan` | 239 |
| `nhom_3_bien_dong.tang` | 12 |
| `nhom_3_bien_dong.giam` | 9 |
| Tổng | 981 |

`bo_tu_vung_CPI_hoan_chinh.json` không có similarity, trạng thái duyệt, nguồn đối chiếu hay metadata. `res.json` được giữ riêng để xem kết quả trước duyệt. Gói gọn này không kèm chương trình tự động duyệt hoặc toàn bộ nhật ký quyết định từng ứng viên; quá trình duyệt ở bước 3 đã thực hiện có người nghiên cứu tham gia.

## 7. Bước làm tiếp theo cho bộ từ vựng

Sau khi hoàn thiện bộ từ vựng, sử dụng file bo_tu_vung_CPI_hoan_chinh.json làm đầu vào cho chương trình thu thập bài báo. Các từ khóa thuộc 11 nhóm CPI và nhóm tác nhân vĩ mô được dùng để tìm kiếm bài viết trên các nguồn báo đã lựa chọn, trong phạm vi thời gian nghiên cứu.
Quy trình thu thập gồm:
1. Đọc các từ khóa từ file JSON và tạo truy vấn tìm kiếm.
2. Thu thập đường dẫn bài viết phù hợp với truy vấn.
3. Truy cập từng bài để lấy tiêu đề, ngày đăng, nguồn báo, URL và nội dung.
4. Loại các bài trùng lặp, bản ghi thiếu nội dung và bài nằm ngoài thời gian nghiên cứu.
5. Đối chiếu tiêu đề và nội dung với bộ từ vựng, lưu các từ khóa khớp cùng nhóm tương ứng để hỗ trợ sàng lọc mức độ liên quan đến CPI.
6. Xuất dữ liệu dưới dạng JSONL, mỗi dòng là một bài báo, phục vụ các bước gán nhãn và trích xuất đặc trưng tiếp theo.
Ở giai đoạn này, ưu tiên thu thập bằng từ khóa thuộc nhóm 1 và nhóm 2. Nhóm từ tăng/giảm được giữ lại để hỗ trợ bước phân tích chiều biến động sau khi có dữ liệu bài báo.

Thông tin trích dẫn do PhoW2V cung cấp:

```bibtex
@inproceedings{phow2v_vitext2sql,
  title = {A Pilot Study of Text-to-SQL Semantic Parsing for Vietnamese},
  author = {Anh Tuan Nguyen and Mai Hoang Dao and Dat Quoc Nguyen},
  booktitle = {Findings of the Association for Computational Linguistics: EMNLP 2020},
  year = {2020},
  pages = {4079--4085}
}
```
