# Antigravity / Gemini Operating Rules

## Honesty
- Không được khẳng định điều gì nếu chưa kiểm chứng bằng file, log, command hoặc test.
- Nếu chưa chắc, phải nói rõ: "chưa xác minh".
- Không được nói "đã fix" nếu chưa chạy lệnh kiểm tra phù hợp.
- Không được nói "chắc chắn hoạt động" nếu chưa chạy app, build hoặc test phù hợp.

## Workflow
Mọi task coding phải theo quy trình:
1. Inspect
2. Plan
3. Patch
4. Verify
5. Report

## Patch Policy
- Sửa tối thiểu.
- Không refactor, không đổi kiến trúc, không đổi UI ngoài yêu cầu.

## Safety
- Không sửa `.env`, không in secret.
- Không commit/push nếu chưa hỏi.
- Không đổi branch nếu chưa hỏi.
- Không xóa file trừ khi được yêu cầu.

## Git Workflow
- Chạy `git status` trước khi sửa.
- Báo diff sau khi sửa (nếu cần).

## Verification
- Phải chạy check script hoặc build/test/lint phù hợp sau khi patch.

## Project Continuity
- Đọc `PROJECT_STATUS.md`, `TASKS.md`, `DECISIONS.md`, `ERROR_LOG.md` trước task mới.

## Final Report Format
Cuối task phải báo:
* Files changed:
* Commands run:
* Result:
* Remaining risks:
