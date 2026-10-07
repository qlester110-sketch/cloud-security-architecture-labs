variable "github_organization" {
  description = "GitHub organization or account that owns the trusted repository."
  type        = string

  validation {
    condition     = length(trimspace(var.github_organization)) > 0 && !strcontains(var.github_organization, "*")
    error_message = "github_organization must be explicit and cannot contain a wildcard."
  }
}

variable "github_repository" {
  description = "Exact GitHub repository allowed to request this role."
  type        = string

  validation {
    condition     = length(trimspace(var.github_repository)) > 0 && !strcontains(var.github_repository, "*")
    error_message = "github_repository must be explicit and cannot contain a wildcard."
  }
}

variable "github_environment" {
  description = "Protected GitHub environment required before credentials are issued."
  type        = string
  default     = "production"

  validation {
    condition     = length(trimspace(var.github_environment)) > 0 && !strcontains(var.github_environment, "*")
    error_message = "github_environment must be explicit and cannot contain a wildcard."
  }
}

variable "role_name" {
  description = "Name of the AWS role trusted by the approved GitHub Actions job."
  type        = string
  default     = "portfolio-production-deployer"
}

variable "max_session_duration" {
  description = "Maximum lifetime, in seconds, of credentials issued to the workflow."
  type        = number
  default     = 3600

  validation {
    condition     = var.max_session_duration >= 900 && var.max_session_duration <= 3600
    error_message = "Keep demo sessions between 15 minutes and one hour."
  }
}
