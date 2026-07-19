variable "region" {
  description = "Alibaba Cloud region."
  type        = string
  default     = "us-west-1"
}

variable "environment" {
  description = "Single deployment environment for Sprint 001."
  type        = string
  default     = "demo"
}

variable "name_prefix" {
  description = "Prefix for provisioned resources."
  type        = string
  default     = "showrunner"
}

variable "availability_zone" {
  description = "ACK VSwitch availability zone."
  type        = string
}

variable "kubernetes_version" {
  description = "ACK Kubernetes version."
  type        = string
  default     = "1.30.1-aliyun.1"
}

variable "worker_instance_type" {
  description = "ACK worker node instance type."
  type        = string
  default     = "ecs.g6.large"
}

variable "worker_password" {
  description = "Temporary worker node login password. Prefer key pair in production."
  type        = string
  sensitive   = true
}
