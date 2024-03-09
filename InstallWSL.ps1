if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Execute este script como administrador." -ForegroundColor Red
    Exit
}

Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
wsl --install -d Ubuntu-22.04

$windowsUsername = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name.Split("\")[-1]

$ubuntuUsername = $windowsUsername
$ubuntuPassword = Read-Host -Prompt "Digite a senha para o usuário Ubuntu" -AsSecureString

wsl -d Ubuntu-22.04 -- bash -c "sudo useradd -m -s /bin/bash $ubuntuUsername && echo $ubuntuUsername:$($ubuntuPassword | ConvertFrom-SecureString) | sudo chpasswd"

Write-Host "Usuário $ubuntuUsername criado com a mesma senha do Windows no Ubuntu WSL." -ForegroundColor Green
