from supabase import Client, create_client

# Please load through the environment in the future
url = "https://apxmldjogrvjvfzaouyl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFweG1sZGpvZ3J2anZmemFvdXlsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY3OTc4NzEyMSwiZXhwIjoxOTk1MzYzMTIxfQ.897wIUqcjkpsOpd6NF-orMhmnyo7-Nj8zVq7VfG08yg"

supabase: Client = create_client(url, key)
