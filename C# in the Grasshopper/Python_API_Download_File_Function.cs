using System;
using System.Collections;
using System.Collections.Generic;

using Rhino;
using Rhino.Geometry;

using Grasshopper;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;

using System.Collections.Specialized;
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
using GH_IO;
using GH_IO.Serialization;
using System.ComponentModel;
using System.Net;
using System.Text;
using System.Threading.Tasks;

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
  private void RunScript(string url, string filelocation, string Element_id, bool Download_it, ref object A)
  {
    if (url == null || Download_it == false) return;

    NameValueCollection nvc = new NameValueCollection();
    nvc.Add("Element_id", Element_id);
    nvc.Add("btn-submit-photo", "Upload");
    //Print(filelocation);
    HttpUploadFile(url, filelocation, "Element_location_file", "image/jpeg", nvc);

    return;
  }

  // <Custom additional code> 
  public void HttpUploadFile(string url, string file, string paramName, string contentType, NameValueCollection nvc) {
    //log.Debug(string.Format("Uploading {0} to {1}", file, url));
    string boundary = "---------------------------" + DateTime.Now.Ticks.ToString("x");
    byte[] boundarybytes = System.Text.Encoding.ASCII.GetBytes("\r\n--" + boundary + "\r\n");

    HttpWebRequest wr = (HttpWebRequest) WebRequest.Create(url);
    wr.ContentType = "multipart/form-data; boundary=" + boundary;
    wr.Method = "POST";
    wr.KeepAlive = true;
    wr.Credentials = System.Net.CredentialCache.DefaultCredentials;

    Stream rs = wr.GetRequestStream();

    string formdataTemplate = "Content-Disposition: form-data; name=\"{0}\"\r\n\r\n{1}";
    foreach (string key in nvc.Keys)
    {
      rs.Write(boundarybytes, 0, boundarybytes.Length);
      string formitem = string.Format(formdataTemplate, key, nvc[key]);
      byte[] formitembytes = System.Text.Encoding.UTF8.GetBytes(formitem);
      rs.Write(formitembytes, 0, formitembytes.Length);
    }
    rs.Write(boundarybytes, 0, boundarybytes.Length);

    string headerTemplate = "Content-Disposition: form-data; name=\"{0}\"; filename=\"{1}\"\r\nContent-Type: {2}\r\n\r\n";
    string header = string.Format(headerTemplate, paramName, file, contentType);
    byte[] headerbytes = System.Text.Encoding.UTF8.GetBytes(header);
    rs.Write(headerbytes, 0, headerbytes.Length);

    FileStream fileStream = new FileStream(file, FileMode.Open, FileAccess.Read);
    byte[] buffer = new byte[4096];
    int bytesRead = 0;
    while ((bytesRead = fileStream.Read(buffer, 0, buffer.Length)) != 0) {
      rs.Write(buffer, 0, bytesRead);
    }
    fileStream.Close();

    byte[] trailer = System.Text.Encoding.ASCII.GetBytes("\r\n--" + boundary + "--\r\n");
    rs.Write(trailer, 0, trailer.Length);
    rs.Close();

    //Print(nvc[0]);

    WebResponse wresp = null;
    try {
      wresp = wr.GetResponse();
      Stream stream2 = wresp.GetResponseStream();
      StreamReader reader2 = new StreamReader(stream2);
      //Print(reader2.ReadToEnd());

      DirectoryInfo info = new DirectoryInfo("C:\\Users\\jason\\Desktop\\Element_files");
      if (!info.Exists) {
        info.Create();
      }

      string path = Path.Combine("C:\\Users\\jason\\Desktop\\Element_files", nvc[0] + ".3dm");
      using(FileStream outputFileStream = new FileStream(path, FileMode.Create)) {
        stream2.CopyTo(outputFileStream);
      }
      Print("Success downloading file");

      return;
      //log.Debug(string.Format("File uploaded, server response is: {0}", reader2.ReadToEnd()));
    } catch(Exception ex) {
      Print("Error downloading file", ex);
      //log.Error("Error uploading file", ex);
      if(wresp != null) {
        wresp.Close();
        wresp = null;
      }
    } finally {
      wr = null;
    }
  }
  // </Custom additional code> 
}