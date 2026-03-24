from app.common.enums import DimensionCode

DEFAULT_DIMENSIONS = [
    (1, DimensionCode.LEGAL_ENTITY.value, "Legal Entity", "الشركة / الكيان القانوني", False),
    (2, DimensionCode.BRANCH.value, "Branch", "الفرع", False),
    (3, DimensionCode.MAIN_ACCOUNT.value, "Main Account", "رقم الحساب الرئيسي", False),
    (4, DimensionCode.COST_CENTER.value, "Cost Center", "مركز التكلفة", False),
    (5, DimensionCode.DEPARTMENT.value, "Department", "القسم / الإدارة", False),
    (6, DimensionCode.PROJECT.value, "Project / Job Order", "المشروع / أمر العمل", False),
    (7, DimensionCode.GEOGRAPHIC_REGION.value, "Geographic Region", "المنطقة الجغرافية", False),
    (8, DimensionCode.BUSINESS_LINE.value, "Business Line / Product", "خط الأعمال / المنتج", False),
    (9, DimensionCode.RESERVE_9.value, "Reserve Dimension 9", "البعد الاحتياطي 9", True),
    (10, DimensionCode.RESERVE_10.value, "Reserve Dimension 10", "البعد الاحتياطي 10", True),
]
