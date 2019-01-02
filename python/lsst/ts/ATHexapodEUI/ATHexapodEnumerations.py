from SALPY_ATHexapod import *

class SummaryStates:
    OfflineState = SAL__STATE_OFFLINE
    StandbyState = SAL__STATE_STANDBY
    DisabledState = SAL__STATE_DISABLED
    EnabledState = SAL__STATE_ENABLED
    FaultState = SAL__STATE_FAULT

class DetailedState:
    InMotionState = ATHexapod_shared_DetailedState_InMotionState
    NotInMotionState = ATHexapod_shared_DetailedState_NotInMotionState

class SummaryState:
    DisabledState = ATHexapod_shared_SummaryState_DisabledState
    EnabledState = ATHexapod_shared_SummaryState_EnabledState
    FaultState = ATHexapod_shared_SummaryState_FaultState
    OfflineState = ATHexapod_shared_SummaryState_OfflineState
    StandbyState = ATHexapod_shared_SummaryState_StandbyState

