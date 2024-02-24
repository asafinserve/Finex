import os
from supabase import create_client, Client

url = "https://bpgwgqutdpivvmzhxqdl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwZ3dncXV0ZHBpdnZtemh4cWRsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDUwNzY0MzUsImV4cCI6MjAyMDY1MjQzNX0.wTfP6ZIYj8PDFGs1Xqct_b4DNMzRJENlocwjikHJpfs"
supabase: Client = create_client(url, key)
data = supabase.table("users").insert({"mail_id":"abhinavsath7@gmail.com", "username":"Abhinav Satheesh", "user_id":1}).execute()
