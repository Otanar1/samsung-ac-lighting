# Samsung AC Display Light (Home Assistant)

Integração customizada para controlar o LED/display de aparelhos de ar-condicionado Samsung
via SmartThings Cloud API.

## Funcionalidades
- Liga/desliga o display (LED)
- Estado real (não otimista)
- Compatível com automações
- Sem hacks ou comandos ocultos

## Instalação (HACS)
1. Adicione este repositório como **Custom Repository**
2. Tipo: Integration
3. Instale
4. Reinicie o Home Assistant

## Configuração (configuration.yaml)

```yaml
switch:
  - platform: samsung_ac_lighting
    token: SEU_SMARTTHINGS_PAT
    device_id: SEU_DEVICE_ID
