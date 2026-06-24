# ====================================
# oms_factory.py
# ====================================

from utils.runtime_mode import (

    RUNTIME_MODE,

    SIMULATION,

    PAPER,

    LIVE
)

from utils.logger import (
    SystemLogger
)

from execution.oms.fake_oms import (
    SimulationOMS
)

from execution.oms.live_oms import (
    LiveOMS
)


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)


# ====================================
# CREATE OMS
# ====================================

def create_oms():

    logger.warning(

        f"Creating OMS | "

        f"Mode={RUNTIME_MODE}"
    )

    # ====================================
    # SIMULATION MODE
    # ====================================

    if RUNTIME_MODE == SIMULATION:

        logger.warning(

            "#################################\n"

            "####### SIMULATION MODE ########\n"

            "#################################"
        )

        return (
            SimulationOMS()
        )

    # ====================================
    # PAPER MODE
    # ====================================

    elif RUNTIME_MODE == PAPER:

        logger.warning(

            "#################################\n"

            "########## PAPER MODE ##########\n"

            "#################################"
        )

        raise NotImplementedError(
            "Paper OMS Not Implemented"
        )

    # ====================================
    # LIVE MODE
    # ====================================

    elif RUNTIME_MODE == LIVE:

        logger.warning(

            "#################################\n"

            "########### LIVE MODE ##########\n"

            "#################################"
        )

        return (
            LiveOMS()
        )

    # ====================================
    # INVALID MODE
    # ====================================

    raise RuntimeError(

        f"Unsupported Runtime Mode | "

        f"{RUNTIME_MODE}"
    )