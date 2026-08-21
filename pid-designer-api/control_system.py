"""
control_system.py

Núcleo matemático do PID Designer.
Não depende de PySide6 nem de Matplotlib.

Entrada:
    dicionário com os mesmos campos produzidos atualmente pelo DataReader.

Saída:
    funções de transferência C, G, H, L e T, além do ganho DC K0.
"""

import control as ctl


class ControlSystem:
    """Modelo matemático do sistema de controle."""

    def __init__(self, data):
        self.data = data

        # Controlador original e controlador editado
        self.C = ctl.tf([1], [1])
        self.CEdt = ctl.tf([1], [1])
        self.CCircuit = ctl.tf([1], [1])

        self.T = None
        self.G = ctl.tf([1], [1])
        self.H = ctl.tf([1], [1])
        self.L = None
        self.K0 = None

        self.mode = data.get("mode", 0)

        self.Kp = 0
        self.Ki = 0
        self.Kd = 0

        self.build_controller()
        self.build_plant()
        self.build_sensor()
        self.build_closed_loop()

    def build_controller(self):
        """Constrói C(s) a partir do modo e dos parâmetros do circuito."""

        s = ctl.TransferFunction.s
        self.mode = self.data.get("mode", 0)

        if self.mode == 0:
            self.Kp = 0
            self.Ki = 0
            self.Kd = 0

            if self.data.get("P_enabled", False):
                self.Kp = self.data["R6"] / self.data["R5"]

            if self.data.get("I_enabled", False):
                self.Ki = 1 / (
                    self.data["R7"] * self.data["C1"]
                )

            if self.data.get("D_enabled", False):
                self.Kd = (
                    self.data["R10"] * self.data["C2"]
                )

            if self.Kp == 0 and self.Ki == 0 and self.Kd == 0:
                self.C = ctl.tf([1], [1])
            else:
                self.C = (
                    self.Kp
                    + self.Ki / s
                    + self.Kd * s
                )

            self.CCircuit = self.C

        else:
            # No modo editado, CEdt é o controlador definido pelo editor
            # de polos e zeros.
            self.C = self.CEdt

    def build_plant(self):
        """Constrói G(s)."""

        self.G = ctl.tf(
            self.data["Gnum"],
            self.data["Gden"]
        )

    def build_sensor(self):
        """Constrói H(s)."""

        self.H = ctl.tf(
            self.data["Hnum"],
            self.data["Hden"]
        )

    def build_closed_loop(self):
        """Calcula L(s), T(s) e o ganho DC."""

        self.L = self.C * self.G * self.H

        self.T = ctl.feedback(
            self.C * self.G,
            self.H
        )

        self.K0 = ctl.dcgain(self.T)

    def get_transfer_functions(self):
        """Retorna os principais modelos matemáticos."""

        return {
            "C": self.C,
            "G": self.G,
            "H": self.H,
            "L": self.L,
            "T": self.T,
            "K0": self.K0,
        }

    def get_pid_gains(self):
        """Retorna os ganhos calculados do controlador PID."""

        return {
            "Kp": self.Kp,
            "Ki": self.Ki,
            "Kd": self.Kd,
        }
