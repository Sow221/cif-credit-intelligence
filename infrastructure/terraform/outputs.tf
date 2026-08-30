output "server_ip" {
  description = "Adresse IPv4 publique du VPS CIF"
  value       = hcloud_server.cif_vps.ipv4_address
}

output "server_status" {
  description = "Etat du serveur"
  value       = hcloud_server.cif_vps.status
}
