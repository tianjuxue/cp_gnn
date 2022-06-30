[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [./nepermesh]
    type = FileMeshGenerator
    file = n2-id1.msh # simulation_fd_single_layer_030.msh
    # file = simulation_fd_single_layer_030.msh # simulation_fd_single_layer_030.msh
    displacements = 'disp_x disp_y disp_z'
    # This MeshModifier currently only works with ReplicatedMesh.
    # For more information, refer to #2129.
    parallel_type = replicated
  [../]

  [./x0_modifier]
    type = BoundingBoxNodeSetGenerator
    input = nepermesh
    new_boundary = x0
    top_right = '0.1 3.1 3.1'
    bottom_left = '-0.1 -0.1 -0.1'
  [../]
  [./y0_modifier]
    type = BoundingBoxNodeSetGenerator
    input = x0_modifier
    new_boundary = y0
    top_right = '3.1 0.1 3.1'
    bottom_left = '-0.1 -0.1 -0.1'
  [../]
  [./z0_modifier]
    type = BoundingBoxNodeSetGenerator
    input = y0_modifier
    new_boundary = z0
    top_right = '3.1 3.1 0.1'
    bottom_left = '-0.1 -0.1 -0.1'
  [../]


  [./x1_modifier]
    type = BoundingBoxNodeSetGenerator
    input = z0_modifier
    new_boundary = x1
    top_right = '3.001 3.1 3.1'
    bottom_left = '2.999 -0.1 -0.1'
  [../]
  [./y1_modifier]
    type = BoundingBoxNodeSetGenerator
    input = x1_modifier
    new_boundary = y1
    top_right = '3.1 3.001 3.1'
    bottom_left = '-0.1 2.999 -0.1'
  [../]
  [./z1_modifier]
    type = BoundingBoxNodeSetGenerator
    input = y1_modifier
    new_boundary = z1
    top_right = '3.1 3.1 3.001'
    bottom_left = '-0.1 -0.1 2.999'
  [../]


[]

[AuxVariables]
  [./pk2]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./fp_zz]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./e_zz]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./gss]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./slip_increment]
   order = CONSTANT
   family = MONOMIAL
  [../]
[]

[Modules/TensorMechanics/Master/all]
  strain = FINITE
  add_variables = true
  generate_output = stress_zz
[]


[UserObjects]
  [./prop_read]
    type = GrainPropertyReadFile
    prop_file_name = 'euler_ang_test.inp'
    # Enter file data as prop#1, prop#2, .., prop#nprop
    nprop = 3
    ngrain = 2
    read_type = indexgrain
  [../]
[]

[AuxKernels]
  [./pk2]
   type = RankTwoAux
   variable = pk2
   rank_two_tensor = second_piola_kirchhoff_stress
   index_j = 2
   index_i = 2
   execute_on = timestep_end
  [../]
  [./fp_zz]
    type = RankTwoAux
    variable = fp_zz
    rank_two_tensor = plastic_deformation_gradient
    index_j = 2
    index_i = 2
    execute_on = timestep_end
  [../]
  [./e_zz]
    type = RankTwoAux
    variable = e_zz
    rank_two_tensor = total_lagrangian_strain
    index_j = 2
    index_i = 2
    execute_on = timestep_end
  [../]
  [./gss]
   type = MaterialStdVectorAux
   variable = gss
   property = slip_resistance
   index = 0
   execute_on = timestep_end
  [../]
  [./slip_inc]
   type = MaterialStdVectorAux
   variable = slip_increment
   property = slip_increment
   index = 0
   execute_on = timestep_end
  [../]
[]

[BCs]
  [./z_bot]
    type = DirichletBC
    variable = disp_z
    boundary = z0
    value = 0.0
  [../]

  [./y_bot]
    type = DirichletBC
    variable = disp_y
    boundary = y0
    value = 0.0
  [../]

  [./x_bot]
    type = DirichletBC
    variable = disp_x
    boundary = x0
    value = 0.0
  [../]


  [./tdisp]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = z1
    function = '0.1*t'
  [../]

  [./y_bot1]
    type = DirichletBC
    variable = disp_y
    boundary = y1
    value = 0.0
  [../]


  [./x_bot1]
    type = DirichletBC
    variable = disp_x
    boundary = x1
    value = 0.0
  [../]

[]
 

[Materials]
  [./elasticity_tensor]
    type = ComputeElasticityTensorCPGrain  # ComputeElasticityTensorConstantRotationCP, ComputeElasticityTensorCPGrain
    C_ijkl = '1.684e5 1.214e5 1.214e5 1.684e5 1.214e5 1.684e5 0.754e5 0.754e5 0.754e5'
    fill_method = symmetric9
    read_prop_user_object = prop_read
  [../]
  [./stress]
    type = ComputeMultipleCrystalPlasticityStress
    crystal_plasticity_models = 'trial_xtalpl'
    tan_mod_type = exact
  [../]
  [./trial_xtalpl]
    type = CrystalPlasticityKalidindiUpdate
    number_slip_systems = 12
    slip_sys_file_name = input_slip_sys.txt
  [../]
[]

[Postprocessors]
  [./stress_zz]
    type = ElementAverageValue
    variable = stress_zz
  [../]
  [./pk2]
   type = ElementAverageValue
   variable = pk2
  [../]
  [./fp_zz]
    type = ElementAverageValue
    variable = fp_zz
  [../]
  [./e_zz]
    type = ElementAverageValue
    variable = e_zz
  [../]
  [./gss]
    type = ElementAverageValue
    variable = gss
  [../]
  [./slip_increment]
   type = ElementAverageValue
   variable = slip_increment
  [../]
[]

[Preconditioning]
  [./smp]
    type = SMP
    full = true
  [../]
[]

[Executioner]
  type = Transient
  solve_type = 'PJFNK'

  petsc_options_iname = '-pc_type -pc_asm_overlap -sub_pc_type -ksp_type -ksp_gmres_restart'
  petsc_options_value = ' asm      2              lu            gmres     200'
  nl_abs_tol = 1e-10
  nl_rel_tol = 1e-10
  nl_abs_step_tol = 1e-10

  start_time = 0.0
  end_time = 0.1
  dt = 0.01

[]

[Outputs]
  exodus = true
[]