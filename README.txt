[English]
Hello, before running this code, you should put this code below in a .bat file and run it where you want your dataset to be. From there, you should run vscode and write this command in the terminal:
---------------------------
streamlit run main.py 
---------------------------
If you don't run it with this, it will give an error + you should also run this code in the terminal:
----------------------------------------------------
pip install streamlit openai pdfplumber pytesseract pdf2image Pillow
----------------------------------------------------
, you must also have the 
"tesseract "program installed 
----------------------------------
Now we come to the code that will execute the files that I could not put due to the security of my own API. Steps to execute this code:
1_Create a text document and write this command in it (you can change the names of the files, but you must also change their names in your Python code)
=======================
@echo off
:: --------- ایجاد فولدر اصلی ---------
mkdir legal_assistant
cd legal_assistant

:: --------- ایجاد فولدر منابع ---------
mkdir sources

:: --------- ایجاد فایل های خالی منابع ---------
type nul > sources\civil.txt
type nul > sources\criminal.txt

:: --------- ایجاد فایل Python اصلی ---------
type nul > main.py

:: --------- ایجاد فایل secrets.toml ---------
echo [general]>secrets.toml
echo OPENAI_API_KEY = "your_openai_api_key_here">>secrets.toml

echo -------------------------------
echo فولدر و فایل های پروژه ساخته شد.
echo legal_assistant\main.py
echo legal_assistant\sources\civil.txt
echo legal_assistant\sources\criminal.txt
echo legal_assistant\secrets.toml
echo -------------------------------
pause

=======================
2_Save the file with the .bat  format and run the file. Your files will be created
And that's all, this program is in Persian.But you can change it to English and other languages ​​by changing the code according to the law of that country.
[فارسی]
سلام قبل از اجرای این کد تو باید این کد پایین رو توی یک فایل .bat بزاری و رانش کنی توی جایی که می خوای دیتا ستت باشه و از اونجا باید vscode رو ران کنی و این دستور رو در ترمینالت بنویسی :
streamlit run main.py 
اگه با این ران نکنی ارور میده + باید این کد هم اجرا کنی توی ترمینالت :
------------------------------------------------------
pip install streamlit openai pdfplumber pytesseract pdf2image Pillow
------------------------------------------------------
, تو باید برنامه 
tesseract هم نصب داشته باشی
حالا می رسیم به کدی که برات فایل هایی که به دلیل امنیت api خودم نتونستم بزارم رو برات انجام میده مراحل اجرای این کد:
1_یه تکست داکیومنت میسازی توش این دستور رو مینویسی(می تونی اسم فایل هارو تغییر بدی اما باید توی کد پایتون هم اسمشون رو عوض کنی)
======================================
@echo off
:: --------- ایجاد فولدر اصلی ---------
mkdir legal_assistant
cd legal_assistant

:: --------- ایجاد فولدر منابع ---------
mkdir sources

:: --------- ایجاد فایل های خالی منابع ---------
type nul > sources\civil.txt
type nul > sources\criminal.txt

:: --------- ایجاد فایل Python اصلی ---------
type nul > main.py

:: --------- ایجاد فایل secrets.toml ---------
echo [general]>secrets.toml
echo OPENAI_API_KEY = "your_openai_api_key_here">>secrets.toml

echo -------------------------------
echo فولدر و فایل های پروژه ساخته شد.
echo legal_assistant\main.py
echo legal_assistant\sources\civil.txt
echo legal_assistant\sources\criminal.txt
echo legal_assistant\secrets.toml
echo -------------------------------
pause
======================================
2_فایل رو با پسوند .bat سیو کن و رانش کد بوم فایل های تو ساخته شدن
و تموم راستی این برنامه فارسی هستش  و من به فارسی بودن اش افتخار می کنم.

