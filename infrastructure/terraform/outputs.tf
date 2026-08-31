output "web_instance_ip" {
  description = "Adresse IP publique de l'instance EC2 (serveur principal)"
  value       = aws_instance.cif_web.public_ip
}

output "web_instance_id" {
  description = "Identifiant de l'instance EC2"
  value       = aws_instance.cif_web.id
}

output "rds_endpoint" {
  description = "Point d'acces a la base de donnees PostgreSQL"
  value       = aws_db_instance.cif_postgres.endpoint
}

output "s3_models_bucket" {
  description = "Nom du bucket S3 de stockage des modeles"
  value       = aws_s3_bucket.cif_models.bucket
}

output "ecr_backend" {
  description = "URI du registre ECR backend"
  value       = aws_ecr_repository.cif_backend.repository_url
}

output "ecr_frontend" {
  description = "URI du registre ECR frontend"
  value       = aws_ecr_repository.cif_frontend.repository_url
}
