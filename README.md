# Claude_translation

使用 Anthropic 提供的 Claude API 進行翻譯。填入自己的 API key，並將想要翻譯的文字存到文章中，即可得到翻譯結果。

## 使用方式

1. 將想要翻譯的文字存到 txt 檔案中。
2. 在同一資料夾下建立 `.env` 檔案，並填入自己的 API key。可以參考 `.env.default`。
3. 修改 `main.ipynb` 中的參數
    - `INPUT_FILE`：欲翻譯的檔案名稱。
    - `OUTPUT_FILE`：翻譯後的檔案名稱，程式執行完後將會產生該檔案。
    - `LANGUAGE`：欲翻譯成的語言。
    - `MODEL`：使用模型。可以參考 [Anthropic 的官方文件](https://docs.anthropic.com/claude/docs/models-overview#model-comparison)
4. 執行 `main.ipynb`。
