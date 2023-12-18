# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "hacker_news_bucket" {
  name          = "hacker-news-bucket"
  location      = "US"
  force_destroy = true

  public_access_prevention = "enforced"
}

resource "google_storage_bucket_object" "hacker_news_code" {
  name   = "function.zip"
  source = "function.zip"
  bucket = google_storage_bucket.hacker_news_bucket.name
}
