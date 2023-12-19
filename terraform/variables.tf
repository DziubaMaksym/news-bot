variable "project" {
  description = "Project ID"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "Region of GCP"
  type        = string
  sensitive   = true
}

variable "mastodon_access_token" {
  description = ""
  type        = string
  sensitive   = true
}
variable "mastodon_api_base_url" {
  description = ""
  type        = string
  sensitive   = true
}
