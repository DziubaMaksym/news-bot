# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
locals {
  bucket_names = {
    "hacker_news_bucket"        = "hacker-news-bucket-askldj878yuhjh",
    "hacker_news_story_id_prod" = "hacker-news-story-id-opqwik128"
  }
}

resource "google_storage_bucket" "hacker_news_buckets" {
  for_each = local.bucket_names

  name                     = each.value
  location                 = "US"
  force_destroy            = true
  public_access_prevention = "enforced"
}

resource "google_storage_bucket_object" "hacker_news_code" {
  name   = "function.zip"
  source = "function.zip"
  bucket = google_storage_bucket.hacker_news_buckets["hacker_news_bucket"].name
}

resource "google_storage_bucket_iam_member" "bucket_permissions" {
  for_each = local.bucket_names

  bucket = google_storage_bucket.hacker_news_buckets[each.key].name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.hacker_news_account.email}"
}

resource "google_storage_bucket_iam_member" "bucket_object_permissions" {
  for_each = local.bucket_names

  bucket = google_storage_bucket.hacker_news_buckets[each.key].name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.hacker_news_account.email}"
}
