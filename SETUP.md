# Setup Documentation

## Requirements
- Python (version TBD)
- GenLayer dependencies (`py-genlayer`, `gltest`)

## Install
- Chạy `python -m venv venv` để tạo môi trường ảo.
- Activate môi trường: `.\venv\Scripts\Activate.ps1` (Windows).
- Cài đặt thư viện: `pip install -r requirements.txt`.

## Run dev
- Đảm bảo đã activate venv: `.\venv\Scripts\Activate.ps1`.

## Build
- Không cần build. Các file `.py` hợp đồng là độc lập.

## Test
- Sử dụng `pytest` trong môi trường ảo.

## Check
- Chạy `./scripts/check.ps1` (Windows) hoặc `./scripts/check.sh` (Linux/Mac).

## Notes for agents
- Các file contract bắt buộc phải theo chuẩn ASCII và cấu trúc strict của GenLayer (như `README.md` đã nêu).
- Không tự ý cài đặt package khi chưa có sự đồng ý của User.
