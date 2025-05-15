import win32com

word_app = win32com.client.Dispatch("Word.Application")
word_app.Visible = True
document = word_app.Documents.Open("tutu.docx")
