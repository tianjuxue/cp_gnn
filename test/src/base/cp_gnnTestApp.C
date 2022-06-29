//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#include "cp_gnnTestApp.h"
#include "cp_gnnApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "MooseSyntax.h"
#include "ModulesApp.h"

InputParameters
cp_gnnTestApp::validParams()
{
  InputParameters params = cp_gnnApp::validParams();
  return params;
}

cp_gnnTestApp::cp_gnnTestApp(InputParameters parameters) : MooseApp(parameters)
{
  cp_gnnTestApp::registerAll(
      _factory, _action_factory, _syntax, getParam<bool>("allow_test_objects"));
}

cp_gnnTestApp::~cp_gnnTestApp() {}

void
cp_gnnTestApp::registerAll(Factory & f, ActionFactory & af, Syntax & s, bool use_test_objs)
{
  cp_gnnApp::registerAll(f, af, s);
  if (use_test_objs)
  {
    Registry::registerObjectsTo(f, {"cp_gnnTestApp"});
    Registry::registerActionsTo(af, {"cp_gnnTestApp"});
  }
}

void
cp_gnnTestApp::registerApps()
{
  registerApp(cp_gnnApp);
  registerApp(cp_gnnTestApp);
}

/***************************************************************************************************
 *********************** Dynamic Library Entry Points - DO NOT MODIFY ******************************
 **************************************************************************************************/
// External entry point for dynamic application loading
extern "C" void
cp_gnnTestApp__registerAll(Factory & f, ActionFactory & af, Syntax & s)
{
  cp_gnnTestApp::registerAll(f, af, s);
}
extern "C" void
cp_gnnTestApp__registerApps()
{
  cp_gnnTestApp::registerApps();
}
