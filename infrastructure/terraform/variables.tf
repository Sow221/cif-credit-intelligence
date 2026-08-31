variable "aws_region" {
  description = "Region AWS de deploiement"
  type        = string
  default     = "eu-west-3"
}

variable "key_name" {
  description = "Nom de la paire de cles SSH EC2 (creee dans la console AWS)"
  type        = string
}

variable "models_bucket_name" {
  description = "Nom globalement unique du bucket S3 des modeles"
  type        = string
}

variable "subnet_ids" {
  description = "Identifiants des sous-reseaux (VPC par defaut) pour RDS et EC2"
  type        = list(string)
}

variable "db_name" {
  description = "Nom de la base de donnees CIF"
  type        = string
  default     = "cif"
}

variable "db_username" {
  description = "Utilisateur de la base de donnees"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Mot de passe de la base de donnees"
  type        = string
  sensitive   = true
}
