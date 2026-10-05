from telemetry import parse_line, data_quality_report

lineas = [
    "1717000012.412|S0001|SESSION_START|player=ana;difficulty=normal",
    "",
    "esto no es valido",
    "1717000031.640|S0001|ENEMY_KILL|type=red;wave=1",
    "1717000045.900|S0001|DAMAGE_TAKEN|=1;source=slime",
    "1717000090.000|S0001|SESSION_END|score=3200;level=4;duration=77.6;result=death",
]

print("Prueba parse_line:")
for linea in lineas:
    resultado = parse_line(linea)
    print(f"  {linea!r} -> {resultado}")

print("\nReporte de calidad actual:")
print(data_quality_report("logs"))
