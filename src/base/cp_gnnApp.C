#include "cp_gnnApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "ModulesApp.h"
#include "MooseSyntax.h"

InputParameters
cp_gnnApp::validParams()
{
  InputParameters params = MooseApp::validParams();

  return params;
}

cp_gnnApp::cp_gnnApp(InputParameters parameters) : MooseApp(parameters)
{
  cp_gnnApp::registerAll(_factory, _action_factory, _syntax);
}

cp_gnnApp::~cp_gnnApp() {}

void
cp_gnnApp::registerAll(Factory & f, ActionFactory & af, Syntax & syntax)
{
  ModulesApp::registerAll(f, af, syntax);
  Registry::registerObjectsTo(f, {"cp_gnnApp"});
  Registry::registerActionsTo(af, {"cp_gnnApp"});

  /* register custom execute flags, action syntax, etc. here */
}

void
cp_gnnApp::registerApps()
{
  registerApp(cp_gnnApp);
}

/***************************************************************************************************
 *********************** Dynamic Library Entry Points - DO NOT MODIFY ******************************
 **************************************************************************************************/
extern "C" void
cp_gnnApp__registerAll(Factory & f, ActionFactory & af, Syntax & s)
{
  cp_gnnApp::registerAll(f, af, s);
}
extern "C" void
cp_gnnApp__registerApps()
{
  cp_gnnApp::registerApps();
}
