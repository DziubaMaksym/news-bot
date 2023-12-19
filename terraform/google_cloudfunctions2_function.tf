# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudfunctions2_function
resource "google_cloudfunctions2_function" "hacker_news" {
  name        = "hacker-news-bot-prod"
  location    = var.region
  description = "A Python function for Hacker News"

  build_config {
    runtime     = "python39"
    entry_point = "hacker_news_function"
    source {
      storage_source {
        bucket = google_storage_bucket.hacker_news_buckets["hacker_news_bucket"].name
        object = google_storage_bucket_object.hacker_news_code.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "128Mi"
    timeout_seconds       = 60
    service_account_email = google_service_account.hacker_news_account.email
    ingress_settings      = "ALLOW_INTERNAL_AND_GCLB"
    environment_variables = {
      "MASTODON_ACCESS_TOKEN" = var.mastodon_access_token
      "MASTODON_API_BASE_URL" = var.mastodon_api_base_url
      "GCS_BUCKET_NAME"       = google_storage_bucket.hacker_news_buckets["hacker_news_story_id_prod"].name
    }
  }
  depends_on = [
    google_service_account.hacker_news_account
  ]

}

resource "google_cloudfunctions2_function_iam_member" "invoker" {
  project        = var.project
  location       = var.region
  cloud_function = google_cloudfunctions2_function.hacker_news.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.hacker_news_account.email}"
  depends_on = [
    google_cloudfunctions2_function.hacker_news
  ]
}

resource "google_cloud_run_service_iam_member" "cloud_run_invoker" {
  project  = var.project
  location = var.region
  service  = google_cloudfunctions2_function.hacker_news.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.hacker_news_account.email}"
}

