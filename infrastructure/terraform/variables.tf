variable "hcloud_token" {
  description = "Token API Hetzner Cloud"
  type        = string
  sensitive   = true
}

variable "ssh_key_id" {
  description = "ID de la cle SSH enregistree sur Hetzner"
  type        = string
}
