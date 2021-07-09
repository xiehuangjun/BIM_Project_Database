using System;
using System.Collections;
using System.Collections.Generic;

using Rhino;
using Rhino.Geometry;

using Grasshopper;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;

using System.IO;
using System.Linq;
using System.Data;
using System.Drawing;
using System.Reflection;
using System.Windows.Forms;
using System.Xml;
using System.Xml.Linq;
using System.Runtime.InteropServices;

using Rhino.DocObjects;
using Rhino.Collections;
using GH_IO;
using GH_IO.Serialization;

/// <summary>
/// This class will be instantiated on demand by the Script component.
/// </summary>
public class Script_Instance : GH_ScriptInstance
{
#region Utility functions
  /// <summary>Print a String to the [Out] Parameter of the Script component.</summary>
  /// <param name="text">String to print.</param>
  private void Print(string text) { /* Implementation hidden. */ }
  /// <summary>Print a formatted String to the [Out] Parameter of the Script component.</summary>
  /// <param name="format">String format.</param>
  /// <param name="args">Formatting parameters.</param>
  private void Print(string format, params object[] args) { /* Implementation hidden. */ }
  /// <summary>Print useful information about an object instance to the [Out] Parameter of the Script component. </summary>
  /// <param name="obj">Object instance to parse.</param>
  private void Reflect(object obj) { /* Implementation hidden. */ }
  /// <summary>Print the signatures of all the overloads of a specific method to the [Out] Parameter of the Script component. </summary>
  /// <param name="obj">Object instance to parse.</param>
  private void Reflect(object obj, string method_name) { /* Implementation hidden. */ }
#endregion

#region Members
  /// <summary>Gets the current Rhino document.</summary>
  private readonly RhinoDoc RhinoDocument;
  /// <summary>Gets the Grasshopper document that owns this script.</summary>
  private readonly GH_Document GrasshopperDocument;
  /// <summary>Gets the Grasshopper script component that owns this script.</summary>
  private readonly IGH_Component Component;
  /// <summary>
  /// Gets the current iteration count. The first call to RunScript() is associated with Iteration==0.
  /// Any subsequent call within the same solution will increment the Iteration count.
  /// </summary>
  private readonly int Iteration;
#endregion

  /// <summary>
  /// This procedure contains the user code. Input parameters are provided as regular arguments,
  /// Output parameters as ref arguments. You don't have to assign output parameters,
  /// they will have a default value.
  /// </summary>
  private void RunScript(string url, object JSON, bool Check_in, ref object A)
  {

    if (url == null || Check_in == false) return;
    //if (Check_in == false) return;

    System.Net.ServicePointManager.Expect100Continue = true;
    System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12; //the auth type

    //var request = System.Net.WebRequest.Create(url);
    // If required by the server, set the credentials.
    //request.Credentials = System.Net.CredentialCache.DefaultCredentials;
    // Get the response.
    //var response = (System.Net.HttpWebResponse) request.GetResponse();
    // Display the status.
    //Console.WriteLine(response.StatusDescription);
    // Get the stream containing content returned by the server.
    //Stream dataStream = response.GetResponseStream();
    // Open the stream using a StreamReader for easy access.
    //StreamReader reader = new StreamReader (dataStream);
    // Read the content.
    //A = reader.ReadToEnd();

    //reader.Close();
    //dataStream.Close();
    //response.Close();

    var request = System.Net.WebRequest.Create(url);
    request.ContentType = "application/json; charset=utf-8";
    request.Method = "POST";
    request.ContentType = "application/json";
    //request.Accept = "application/json";

    using(var streamWriter = new StreamWriter(request.GetRequestStream()))
    {
      //string json = JSON;
      streamWriter.Write(JSON);
      streamWriter.Flush();
      streamWriter.Close();
    }

    try
    {
      var httpResponse = (System.Net.HttpWebResponse) request.GetResponse();
      using(var streamReader = new StreamReader(httpResponse.GetResponseStream()))
      {
        var result = streamReader.ReadToEnd();
        A = result;
      }
    }
    catch (System.Net.WebException e)
    {
      Print(e.Message);
    }
  }

  // <Custom additional code> 

  // </Custom additional code> 
}
