# E-commerce Inventory System Setup Guide

這份文件說明如何在本地端建立並執行此專案的開發環境。
本專案分為後端 (FastAPI) 與前端 (Vue 3 + Vite)。

## Prerequisites (前置需求)

請確保您的電腦已安裝以下軟體：

*   **Python**: 3.10 或更高版本
*   **Node.js**: 18.0.0 或更高版本 (建議使用 LTS)
*   **Git**

---

## Backend Setup (後端設定)

後端位於 `backend/` 目錄，使用 Python FastAPI 與 SQLite (本地開發)。

1.  **進入後端目錄**
    ```bash
    cd backend
    ```

2.  **建立虛擬環境 (Virtual Environment)**
    建議使用虛擬環境來管理 Python 套件。
    
    *   Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   macOS / Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **安裝依賴套件**
    ```bash
    pip install -r requirements.txt
    ```

4.  **初始化資料庫**
    執行以下指令來建立 SQLite 資料庫檔案 (`sql_app.db`) 與資料表。
    ```bash
    python create_db.py
    ```

5.  **啟動後端伺服器**
    使用 `uvicorn` 啟動開發伺服器。
    ```bash
    uvicorn main:app --reload
    ```
    伺服器預設會在 `http://localhost:8000` 啟動。
    - API 文件 (Swagger UI): `http://localhost:8000/docs`

---

## Frontend Setup (前端設定)

前端位於 `frontend/` 目錄，使用 Vue 3, Vite 與 TailwindCSS。

1.  **進入前端目錄** (開啟新的終端機視窗)
    ```bash
    cd frontend
    ```

2.  **安裝依賴套件**
    ```bash
    npm install
    ```

3.  **啟動開發伺服器**
    ```bash
    npm run dev
    ```
    啟動後，終端機將顯示訪問網址，通常為 `http://localhost:5173`。

---

## Running the Application (執行應用程式)

1.  確保 **後端** 伺服器正在執行 (`http://localhost:8000`)。
2.  確保 **前端** 伺服器正在執行 (`http://localhost:5173`)。
3.  打開瀏覽器訪問前端網址 (e.g., `http://localhost:5173`) 即可開始使用。

## Notes

*   若遇到 CORS 問題，請檢查 `backend/main.py` 中的 `origins` 設定是否包含您的前端網址。
*   資料庫預設使用 SQLite，檔案為 `backend/sql_app.db`。
