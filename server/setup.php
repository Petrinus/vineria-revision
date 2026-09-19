<?php
declare(strict_types=1);
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require __DIR__.'/core.php';
$initial=getenv('VDE_INITIAL_PASSWORD')?:'';
if(strlen($initial)<6){fwrite(STDERR,"Set VDE_INITIAL_PASSWORD privately for the initial installation. No password is built into this code.\n");exit(1);}
$dir=private_dir();if(is_file($dir.'/state.json')){fwrite(STDERR,"Existing installation will not be overwritten.\n");exit(1);}if(!is_dir($dir))mkdir($dir,0700,true);
$seed=json_decode(file_get_contents(PROJECT.'/src/catalog.json'),true,512,JSON_THROW_ON_ERROR);$users=[];
foreach(['Buñol','Kraft']as$name){$id=bin2hex(random_bytes(12));$users[$id]=['id'=>$id,'name'=>$name,'hash'=>password_digest($initial),'role'=>'admin','active'=>true,'must_change'=>true,'version'=>bin2hex(random_bytes(12))];}
$state=['revision'=>1,'users'=>$users,'catalog'=>$seed,'attempts'=>[],'history'=>[],'audit'=>[],'published_at'=>null];
$file=$dir.'/state.json';$fh=fopen($file,'x');if(!$fh)throw new RuntimeException('State already exists.');chmod($file,0600);fwrite($fh,json_encode($state,JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT|JSON_THROW_ON_ERROR));fclose($fh);
$public=PROJECT.'/site/verwaltung';if(!is_dir($public))mkdir($public,0755,true);
file_put_contents($public.'/index.php',"<?php require __DIR__.'/../../server/admin.php';\n");
file_put_contents($public.'/.htaccess',"DirectoryIndex index.php\n<IfModule mod_rewrite.c>\nRewriteEngine On\nRewriteRule ^index\\.html$ index.php [L]\n</IfModule>\n");
fwrite(STDOUT,"Created Buñol and Kraft. First sign-in requires an individual new password. Initial password was not printed or stored in plaintext.\n");
