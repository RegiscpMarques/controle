"""
main.py
API HTTP para o núcleo matemático do PID Designer.

Executar:
    uvicorn main:app --reload

Endpoint inicial:
    POST /simulate
"""

from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from control_system import ControlSystem
from data_reader import DataReader


app = FastAPI(
    title="PID Designer API",
    version="0.1.0",
    description="Serviço matemático para a aplicação web PID Designer.",
)


class SimulationRequest(BaseModel):
    R5: str
    R6: str
    R7: str
    R10: str

    C1: str
    C2: str

    Gnum: List[float]
    Gden: List[float]

    Hnum: List[float]
    Hden: List[float]

    P_enabled: bool = True
    I_enabled: bool = True
    D_enabled: bool = True
    mode: int = Field(default=0, ge=0)


def transfer_function_to_json(tf):
    """Converte TransferFunction em numerador/denominador estruturados."""

    # Para SISO, python-control armazena os coeficientes como:
    # tf.num[0][0] e tf.den[0][0].
    num = [float(x) for x in tf.num[0][0]]
    den = [float(x) for x in tf.den[0][0]]

    return {
        "num": num,
        "den": den,
    }


def complex_to_json(value):
    """Representa um número real ou complexo de forma serializável."""

    value = complex(value)

    if abs(value.imag) < 1e-12:
        return float(value.real)

    return {
        "real": float(value.real),
        "imag": float(value.imag),
    }


def transfer_function_details(tf):
    """Retorna representação estruturada e polos/zeros."""

    return {
        "num": [float(x) for x in tf.num[0][0]],
        "den": [float(x) for x in tf.den[0][0]],
        "zeros": [complex_to_json(z) for z in tf.zeros()],
        "poles": [complex_to_json(p) for p in tf.poles()],
    }


@app.get("/")
def root():
    return {
        "service": "PID Designer API",
        "status": "ok",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/simulate")
def simulate(request: SimulationRequest):
    """Constrói o sistema e devolve seus resultados matemáticos."""

    try:
        data = {
            "R5": DataReader.parse_component(request.R5),
            "R6": DataReader.parse_component(request.R6),
            "R7": DataReader.parse_component(request.R7),
            "R10": DataReader.parse_component(request.R10),

            "C1": DataReader.parse_component(request.C1),
            "C2": DataReader.parse_component(request.C2),

            "Gnum": request.Gnum,
            "Gden": request.Gden,
            "Hnum": request.Hnum,
            "Hden": request.Hden,

            "P_enabled": request.P_enabled,
            "I_enabled": request.I_enabled,
            "D_enabled": request.D_enabled,
            "mode": request.mode,
        }

        system = ControlSystem(data)

        return {
            "status": "ok",

            "controller": transfer_function_details(system.C),
            "plant": transfer_function_details(system.G),
            "sensor": transfer_function_details(system.H),
            "loop": transfer_function_details(system.L),
            "closed_loop": transfer_function_details(system.T),

            "pid": system.get_pid_gains(),

            "dc_gain": float(system.K0),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
