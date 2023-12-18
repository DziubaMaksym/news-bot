terraform {
  required_version = "> 0.12"
  backend "gcs" {
    bucket = "hacker_news_tf_state"
    prefix = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.9.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}
