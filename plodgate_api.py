from pydantic import BaseModel, Required, Field
from typing import Union, Optional


class PatientInfo(BaseModel):
    event_id: str = Field(..., min_length=1)
    patient_id: str = Field(..., min_length=1)
    when: Optional[str] = Field(None,
                                description="いつごろ？例: 朝, 昼, 夜")
    time: Optional[str] = Field(None,
                                description="時刻。例: 9:30, 夕方4時")
    duration: Optional[str] = Field(None,
                                    description="時間。例: 30分, 1時間")
    where: str = Field(Required,
                       description="場所。例: 勤務先, 駅前のセブンイレブン")
    coordinates: Optional[str] = Field(None,
                                       description="座標。")
    what: str = Field(Required,
                      description="何をしたか？例: 通勤、バイト")
    detail: Optional[str] = Field(None,
                                  description="具体的な内容。例: バス、カラオケボックス")
    who: Optional[str] = Field(None,
                               description="誰と？本人含む。例: 友人、家族")
    other: Optional[str] = Field(None,
                                 description="自由記述")

class PatientInfoContainer(BaseModel):
    __root__: list[PatientInfo]


