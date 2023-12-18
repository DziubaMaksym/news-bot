resource "google_service_account" "hacker_news_account" {
  account_id   = "hacker-news"
  display_name = "Prod Service Account"
}
