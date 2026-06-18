from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="role",
            field=models.CharField(
                choices=[("student", "Etudiant"), ("teacher", "Enseignant")],
                default="student",
                max_length=20,
                verbose_name="role",
            ),
        ),
        migrations.AlterField(
            model_name="studentprofile",
            name="level",
            field=models.CharField(blank=True, max_length=80, verbose_name="niveau ou fonction"),
        ),
        migrations.AlterField(
            model_name="studentprofile",
            name="program",
            field=models.CharField(blank=True, max_length=120, verbose_name="filiere ou departement"),
        ),
        migrations.AlterField(
            model_name="studentprofile",
            name="student_number",
            field=models.CharField(blank=True, max_length=30, verbose_name="matricule ou identifiant"),
        ),
        migrations.AlterModelOptions(
            name="studentprofile",
            options={
                "verbose_name": "profil academique",
                "verbose_name_plural": "profils academiques",
            },
        ),
    ]
