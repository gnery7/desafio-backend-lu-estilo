import re
from fastapi import HTTPException
from pydantic import EmailStr


def validate_cpf(cpf: str) -> bool:
    """
    Valida um CPF no formato brasileiro.
    Retorna True se válido, senão levanta HTTPException.
    """
    cpf = re.sub(r'\D', '', cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise HTTPException(status_code=400, detail="CPF inválido")

    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != int(cpf[i]):
            raise HTTPException(status_code=400, detail="CPF inválido")

    return True


def validate_email(email: EmailStr) -> bool:
    """
    Valida o formato de um email. Se inválido, o Pydantic já levanta erro.
    Aqui só deixamos explícito.
    """
    return True  # Apenas força a validação do tipo EmailStr


def send_whatsapp_message_to(client, message: str) -> dict:
    """
    Simula o envio de uma mensagem de WhatsApp para o cliente.
    """
    print(f"Simulando envio de WhatsApp para {client.name} ({client.id}): {message}")
    return {"status": "200 OK", "mensagem": f"Mensagem enviada para {client.name}"}
