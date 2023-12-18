terraform {
  required_version = "> 0.12"
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
