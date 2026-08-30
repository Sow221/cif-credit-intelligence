terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

# VPS unique (2 vCPU, 2 Go RAM - 3,79 EUR/mois)
resource "hcloud_server" "cif_vps" {
  name        = "cif-credit-production"
  image       = "ubuntu-22.04"
  server_type = "cpx11"

  ssh_keys = [var.ssh_key_id]

  labels = {
    project = "cif-credit-intelligence"
    role    = "production"
  }
}
