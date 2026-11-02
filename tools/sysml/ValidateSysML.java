import java.nio.file.*;
import org.omg.sysml.interactive.SysMLInteractive;
public class ValidateSysML {
  public static void main(String[] args) throws Exception {
    var sysml=SysMLInteractive.createInstance();
    sysml.loadLibrary(args[0]);
    sysml.setResource("aegis-validation.sysml");
    var source=new StringBuilder();
    for(int i=1;i<args.length;i++) {
      System.out.println("SOURCE "+args[i]+" begins at combined line "+(source.toString().lines().count()+1));
      source.append("// SOURCE ").append(args[i]).append("\n").append(Files.readString(Path.of(args[i]))).append("\n");
    }
    Files.createDirectories(Path.of("build/sysml"));
    Files.writeString(Path.of("build/sysml/validated-input.sysml"),source.toString());
    sysml.parse(source.toString());
    int errors=0,warnings=0;
    for(var issue:sysml.validate()) {
      System.out.println(issue.getSeverity()+" line "+issue.getLineNumber()+": "+issue.getMessage());
      if(issue.getSeverity().toString().equals("ERROR")) errors++;
      if(issue.getSeverity().toString().equals("WARNING")) warnings++;
    }
    System.out.println("SEMANTIC_ERRORS="+errors+" WARNINGS="+warnings);
    System.exit(errors==0?0:1);
  }
}
