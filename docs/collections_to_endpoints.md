### Geographic and Organization Collections → Endpoints (Mapped from Swagger)

| รายการ                  | Collection Name             | 📌 Swagger Endpoint                                 |
|------------------------|-----------------------------|---------------------------------------------------|
| Hospital (Organization)| `AMY.hospitals`             | `GET /admin/master-data/organization`             |
| Sub-District           | `AMY.sub_districts`         | `GET /admin/master-data/sub_district`             |
| District               | `AMY.districts`             | `GET /admin/master-data/district`                 |
| Province               | `AMY.provinces`             | `GET /admin/master-data/province`                 |

---

### Patient and Device Collections → Endpoints

| รายการ                          | Collection                    | 📌 Swagger Endpoint                        |
|---------------------------------|-------------------------------|--------------------------------------------|
| Patient                         | `AMY.patients`                | `GET /admin/patients`                      |
| AVA4 (Box)                      | `AMY.amy_boxes`               | `GET /api/ava4/devices`                    |
| AVA4 Sub-device                 | `AMY.amy_devices`             | `GET /api/ava4/sub-devices`               |
| Kati Watch                      | `AMY.watches`                 | `GET /api/kati/devices`                    |
| Qube-Vital (โรงพยาบาล)          | `AMY.mfc_hv01_boxes`          | `GET /api/qube-vital/devices`             |

---

### Medical History Collections → Endpoints

| รายการ                          | Collection                         | 📌 Swagger Endpoint                                               |
|--------------------------------|------------------------------------|------------------------------------------------------------------|
| Blood Pressure History          | `AMY.blood_pressure_histories`     | `GET /admin/medical-history/blood_pressure_histories`           |
| Blood Sugar History             | `AMY.blood_sugar_histories`        | `GET /admin/medical-history/blood_sugar_histories`              |
| Body Data History               | `AMY.body_data_histories`          | `GET /admin/medical-history/body_data_histories`                |
| Creatinine History              | `AMY.creatinine_histories`         | `GET /admin/medical-history/creatinine_histories`               |
| Lipid History                   | `AMY.lipid_histories`              | `GET /admin/medical-history/lipid_histories`                    |
| Sleep Data History              | `AMY.sleep_data_histories`         | `GET /admin/medical-history/sleep_data_histories`               |
| SPO2 History                    | `AMY.spo2_histories`               | `GET /admin/medical-history/spo2_histories`                     |
| Step History                    | `AMY.step_histories`               | `GET /admin/medical-history/step_histories`                     |
| Temperature Data History        | `AMY.temprature_data_histories`    | `GET /admin/medical-history/temprature_data_histories`          |
| Admit Data History              | `AMY.admit_data_histories`         | `GET /admin/medical-history/admit_data_histories`               |
| Allergy History                 | `AMY.allergy_histories`            | `GET /admin/medical-history/allergy_histories`                  |
| Medication History              | `AMY.medication_histories`         | `GET /admin/medical-history/medication_histories`               |
| Underlying Disease History      | `AMY.underlying_disease_histories` | `GET /admin/medical-history/underlying_disease_histories`       |
| Sleep History (Empty)           | `AMY.sleep_histories`              | `GET /admin/medical-history/sleep_histories`                    |

