# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudfunctions2_function
resource "google_cloudfunctions2_function" "hacker_news" {
  name        = "hacker-news-bot"
  location    = var.region
  description = "A Python function for Hacker News"

  build_config {
    runtime     = "python39"
    entry_point = "hacker_news_function"
    source {
      storage_source {
        bucket = google_storage_bucket.hacker_news_bucket.name
        object = google_storage_bucket_object.hacker_news_code.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "128M"
    timeout_seconds       = 60
    service_account_email = google_service_account.hacker_news_account.email
  }
}

resource "google_cloudfunctions2_function_iam_member" "invoker" {
  project        = var.project
  location       = var.region
  cloud_function = google_cloudfunctions2_function.hacker_news.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.hacker_news_account.email}"
}
