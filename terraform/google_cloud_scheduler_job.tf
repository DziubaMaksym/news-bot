resource "google_cloud_scheduler_job" "cloud_function_trigger" {
  name        = "hacker-news-function-trigger"
  description = "Trigger Hacker News function every 25 minutes"
  schedule    = "*/25 * * * *"
  time_zone   = "Etc/UTC"

  http_target {
    uri         = "${google_cloudfunctions2_function.hacker_news.service_config[0].uri}/"
    http_method = "GET"
    oidc_token {
      audience              = "${google_cloudfunctions2_function.hacker_news.service_config[0].uri}/"
      service_account_email = google_service_account.hacker_news_account.email
    }
  }
}

