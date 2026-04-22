import 'package:freezed_annotation/freezed_annotation.dart';

part 'question.freezed.dart';

enum Alternative { A, B, C, D }

enum LawArea {
  direitoConstitucional,
  direitosHumanos,
  eticaProfissional,
  filosofiaDoDireito,
  direitoInternacional,
  direitoTributario,
  direitoAdministrativo,
  direitoAmbiental,
  direitoCivil,
  direitoDoConsumidor,
  eca,
  direitoEmpresarial,
  direitoPenal,
  direitoProcessualCivil,
  direitoProcessualPenal,
  direitoDoTrabalho,
  direitoProcessualDoTrabalho,
  direitoPrevidenciario,
  direitoFinanceiro;

  static final _snakeMap = {
    'direito_constitucional': LawArea.direitoConstitucional,
    'direitos_humanos': LawArea.direitosHumanos,
    'etica_profissional': LawArea.eticaProfissional,
    'filosofia_do_direito': LawArea.filosofiaDoDireito,
    'direito_internacional': LawArea.direitoInternacional,
    'direito_tributario': LawArea.direitoTributario,
    'direito_administrativo': LawArea.direitoAdministrativo,
    'direito_ambiental': LawArea.direitoAmbiental,
    'direito_civil': LawArea.direitoCivil,
    'direito_do_consumidor': LawArea.direitoDoConsumidor,
    'eca': LawArea.eca,
    'direito_empresarial': LawArea.direitoEmpresarial,
    'direito_penal': LawArea.direitoPenal,
    'direito_processual_civil': LawArea.direitoProcessualCivil,
    'direito_processual_penal': LawArea.direitoProcessualPenal,
    'direito_do_trabalho': LawArea.direitoDoTrabalho,
    'direito_processual_do_trabalho': LawArea.direitoProcessualDoTrabalho,
    'direito_previdenciario': LawArea.direitoPrevidenciario,
    'direito_financeiro': LawArea.direitoFinanceiro,
  };

  static LawArea fromJson(String value) =>
      _snakeMap[value] ?? LawArea.direitoConstitucional;

  String get label => switch (this) {
        direitoConstitucional => 'Constitucional',
        direitosHumanos => 'Direitos Humanos',
        eticaProfissional => 'Ética Profissional',
        filosofiaDoDireito => 'Filosofia do Direito',
        direitoInternacional => 'Internacional',
        direitoTributario => 'Tributário',
        direitoAdministrativo => 'Administrativo',
        direitoAmbiental => 'Ambiental',
        direitoCivil => 'Civil',
        direitoDoConsumidor => 'Consumidor',
        eca => 'ECA',
        direitoEmpresarial => 'Empresarial',
        direitoPenal => 'Penal',
        direitoProcessualCivil => 'Proc. Civil',
        direitoProcessualPenal => 'Proc. Penal',
        direitoDoTrabalho => 'Trabalho',
        direitoProcessualDoTrabalho => 'Proc. Trabalho',
        direitoPrevidenciario => 'Previdenciário',
        direitoFinanceiro => 'Financeiro',
      };
}

@freezed
class Question with _$Question {
  const factory Question({
    required String id,
    required String examId,
    required String statement,
    required LawArea area,
    required String alternativeA,
    required String alternativeB,
    required String alternativeC,
    required String alternativeD,
    required List<String> tags,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Question;

  const Question._();

  String alternativeText(Alternative alt) => switch (alt) {
        Alternative.A => alternativeA,
        Alternative.B => alternativeB,
        Alternative.C => alternativeC,
        Alternative.D => alternativeD,
      };
}
