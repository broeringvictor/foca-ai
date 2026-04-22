#!/usr/bin/env bash
# Script de setup inicial do projeto FocaAI Flutter
# Pré-requisito: Flutter SDK instalado (https://flutter.dev/docs/get-started/install)

set -e

echo "==> Instalando dependências..."
flutter pub get

echo "==> Gerando código (freezed, json_serializable, riverpod_generator)..."
dart run build_runner build --delete-conflicting-outputs

echo "==> Verificando análise estática..."
flutter analyze

echo ""
echo "✓ Setup concluído!"
echo ""
echo "Para rodar na Web:"
echo "  flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000"
echo ""
echo "Para rodar no Android/iOS:"
echo "  flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000"
