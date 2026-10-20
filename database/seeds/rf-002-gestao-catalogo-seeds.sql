-- database/seeds/rf-002-produtos-seeds.sql
-- Carga inicial com 20 produtos para o ERP de Materiais de Construção

INSERT INTO produtos (nome, descricao, valor_venda, sku, ativo, criado_por)
VALUES 
    (
        'Cimento CP II-E-32 50kg',
        'Cimento Portland composto com escória, ideal para concreto e argamassa.',
        38.50,
        'MAT-CIM-001',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Tijolo Cerâmico 8 Furos 9x19x19cm (Milheiro)',
        'Milheiro de tijolo cerâmico para alvenaria de vedação.',
        890.00,
        'MAT-TIJ-002',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Areia Média Lavada (m³)',
        'Areia média lavada para assentamento e concreto.',
        110.00,
        'MAT-ARE-003',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Brita 1 (m³)',
        'Pedra britada nº 1 para fabricação de concreto estrutural.',
        125.00,
        'MAT-BRI-004',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Argamassa AC-II Cinza 20kg',
        'Argamassa colante para pisos cerâmicos internos e externos.',
        24.90,
        'MAT-ARG-005',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Rejunte Cerâmico Branco 1kg',
        'Rejunte base cimento para juntas de 1 a 10mm.',
        8.50,
        'MAT-REJ-006',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Vergalhão CA-50 10mm (3/8") 12m',
        'Barra de aço nervurada para armações de concreto armado.',
        44.90,
        'MAT-ACO-007',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Vergalhão CA-60 4.2mm 12m',
        'Barra de aço trefilada para estribos e lajes.',
        12.80,
        'MAT-ACO-008',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Arame Recozido 18 (Rolo 1kg)',
        'Arame galvanizado recozido para amarração de ferragens.',
        18.00,
        'MAT-ARA-009',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Tubo PVC Soldável 25mm (3/4") 6m',
        'Tubo rígido para condução de água fria predial.',
        22.50,
        'HID-TUB-010',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Joelho 90° PVC Soldável 25mm',
        'Conexão curva para água fria.',
        1.75,
        'HID-CON-011',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Caixa D''Água Polietileno 1000L',
        'Reservatório de água com tampa rosqueável.',
        389.00,
        'HID-CAI-012',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Fio Flexível 2.5mm² 750V Azul (Rolo 100m)',
        'Condutor de cobre antichama para circuitos de tomadas.',
        195.00,
        'ELE-FIO-013',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Disjuntor Bipolar Din 20A Curva C',
        'Dispositivo contra sobrecarga e curto-circuito.',
        32.90,
        'ELE-DIS-014',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Tinta Látex Acrílica Fosca Branco Neve 18L',
        'Tinta para paredes internas e externas, acabamento fosco.',
        279.90,
        'TIN-LAT-015',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Massa Corrida PVA 25kg',
        'Massa para nivelamento e correção de paredes internas.',
        54.00,
        'TIN-MAS-016',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Telha Cerâmica Romana (Milheiro)',
        'Telha de barro cozido resinada para cobertura residencial.',
        1650.00,
        'COB-TEL-017',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Bloco de Concreto Estrutural 14x19x39cm',
        'Unidade de bloco para fundações e alvenaria estrutural.',
        4.80,
        'MAT-BLO-018',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Impermeabilizante Asfáltico Neutrol 18L',
        'Pintura asfáltica para proteção de alicerces e baldrames.',
        189.90,
        'IMP-NEU-019',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    ),
    (
        'Piso Cerâmico Esmaltado 60x60cm (Caixa 2.20m²)',
        'Revestimento cerâmico brilhante para pisos internos.',
        72.60,
        'REV-PIS-020',
        TRUE,
        (SELECT id FROM users LIMIT 1)
    );