# techaux_ad (Unified Role)

Build AD OUs (Countries/States/Cities, Departments, GPOs, redirects) and load People (users, groups, manager) in one role.

## Requirements
- Collections: community.windows, ansible.windows
- WinRM to a Domain Controller (Domain Admin)

## Variables
- Keep using your vars: `ad_domain_name`, `ad_root_ou`, `ad_departments`, `ad_geo_cities`, etc.
- Flags: `enable_ou: true/false`, `enable_people: true/false`.

## Example play
```yaml
- hosts: dc
  gather_facts: no
  roles:
    - role: techaux_ad
      vars:
        ad_domain_name: "techaux.local"
        ad_root_ou: "CORP"
        enable_ou: true
        enable_people: true
