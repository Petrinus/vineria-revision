<?php
declare(strict_types=1);
/** Server component. Never place this directory inside the public document root. */
const PROJECT = __DIR__.'/..';
function private_dir(): string {return getenv('VDE_PRIVATE_DIR') ?: PROJECT.'/private';}
function boom(string $s,int $code=400): never {throw new RuntimeException($s,$code);}
function h(mixed $x): string{return htmlspecialchars((string)$x,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');}
function tx(callable $fn,bool $write=true): mixed {
 $dir=private_dir();if(!is_dir($dir)&&!mkdir($dir,0700,true))boom('Speicher nicht verfügbar.',503);
 $lock=fopen($dir.'/lock','c');if(!$lock||!flock($lock,LOCK_EX))boom('Speicher gesperrt.',503);
 try{$file=$dir.'/state.json';$s=is_file($file)?json_decode(file_get_contents($file),true,512,JSON_THROW_ON_ERROR):null;
  if(!$s)boom('Verwaltung noch nicht installiert.',503);$r=$fn($s);
  if($write){$tmp=tempnam($dir,'vde-');chmod($tmp,0600);$json=json_encode($s,JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT|JSON_THROW_ON_ERROR);if(file_put_contents($tmp,$json,LOCK_EX)!==strlen($json)||!rename($tmp,$file))boom('Speichern fehlgeschlagen.',503);}return $r;
 }finally{flock($lock,LOCK_UN);fclose($lock);}
}
function password_digest(string $p): string{return password_hash($p,defined('PASSWORD_ARGON2ID')?PASSWORD_ARGON2ID:PASSWORD_DEFAULT);}
function normalize_username(string $u): string {if(class_exists('Normalizer'))$u=Normalizer::normalize($u,Normalizer::FORM_C);return function_exists('mb_strtolower')?mb_strtolower(trim($u),'UTF-8'):strtolower(trim($u));}
function begin_session(): void {
 if(session_status()===PHP_SESSION_ACTIVE)return;
 ini_set('session.use_strict_mode','1');session_name('vde_team');
 session_set_cookie_params(['lifetime'=>0,'path'=>'/','secure'=>(getenv('VDE_LOCAL_TEST')!=='1'),'httponly'=>true,'samesite'=>'Strict']);session_start();
 $_SESSION['csrf']??=bin2hex(random_bytes(32));
 header('Cache-Control: no-store, private');header('X-Content-Type-Options: nosniff');header('X-Frame-Options: DENY');header('Referrer-Policy: no-referrer');header("Content-Security-Policy: default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; base-uri 'none'");
}
function csrf_check():void {if(!isset($_POST['csrf'])||!is_string($_POST['csrf'])||!hash_equals($_SESSION['csrf']??'',$_POST['csrf']))boom('Sitzung abgelaufen. Neu laden.',403);
 $origin=$_SERVER['HTTP_ORIGIN']??'';$expected=getenv('VDE_ORIGIN')?:'';if($origin!==''&&$expected!==''&&!hash_equals(rtrim($expected,'/'),$origin))boom('Fremde Anfrage abgelehnt.',403);
}
function current_user(array $s): ?array {
 $u=$s['users'][$_SESSION['uid']??'']??null;if(!$u||!$u['active']||($_SESSION['version']??'')!==$u['version']||time()-($_SESSION['last_seen']??0)>1800){unset($_SESSION['uid']);return null;}$_SESSION['last_seen']=time();return$u;
}
function login_attempt(string $username,string $password): bool {
 $result=tx(function(&$s)use($username,$password){$now=time();$key=hash('sha256',($_SERVER['REMOTE_ADDR']??'local'));$attempt=$s['attempts'][$key]??['count'=>0,'since'=>$now];if($now-$attempt['since']>900)$attempt=['count'=>0,'since'=>$now];
  if($attempt['count']>=8)return ['error'=>'Bitte später erneut versuchen.'];$attempt['count']++;$s['attempts'][$key]=$attempt;
  foreach($s['attempts']as$k=>$r)if($now-$r['since']>3600)unset($s['attempts'][$k]);
  $found=null;foreach($s['users']as$id=>$u)if(normalize_username($u['name'])===normalize_username($username)){$found=$u;break;}
  $valid=$found&&$found['active']&&password_verify($password,$found['hash']);if(!$valid)return ['error'=>'Benutzername oder Passwort nicht korrekt.'];unset($s['attempts'][$key]);return ['user'=>$found];});
 if(isset($result['error']))boom($result['error'],429);$u=$result['user'];session_regenerate_id(true);$_SESSION['uid']=$u['id'];$_SESSION['version']=$u['version'];$_SESSION['last_seen']=time();$_SESSION['csrf']=bin2hex(random_bytes(32));return true;
}
function valid_text(mixed $v,int $max=2000): string {if(!is_string($v)||strlen($v)>$max||str_contains($v,"\0"))boom('Ungültiger Text.');return trim($v);}
function cents(mixed $v): int {if(!is_string($v)||!preg_match('/^\d{1,5}([.,]\d{1,2})?$/D',trim($v)))boom('Preis als Zahl, z. B. 6,90 eingeben.');$parts=explode('.',str_replace(',','.',trim($v)));return (int)$parts[0]*100+(int)str_pad($parts[1]??'',2,'0');}
function number(mixed $v,int $min,int $max):int {if(!is_string($v)||!preg_match('/^\d+$/D',$v))boom('Ungültige Menge.');$n=(int)$v;if($n<$min||$n>$max)boom('Menge außerhalb des erlaubten Bereichs.');return$n;}
function strong_password(string $p):void {if(strlen($p)<12||strlen($p)>200)boom('Bitte ein eigenes Passwort mit mindestens 12 Zeichen wählen.');}
function version_check(array $s):void {if((string)($s['revision']??0)!==(string)($_POST['revision']??''))boom('Inzwischen geändert. Bitte neu laden, bevor Sie speichern.',409);}
function audit(array &$s,string $action,array $u):void {$s['audit'][]=['at'=>gmdate('c'),'action'=>$action,'user'=>$u['name']];$s['audit']=array_slice($s['audit'],-100);$s['revision']++;}
function save_snapshot(array &$s):void {$s['history'][]=['at'=>gmdate('c'),'catalog'=>$s['catalog']];$s['history']=array_slice($s['history'],-12);}
function handle_action(string $action):void {
 csrf_check();if($action==='login'){login_attempt(valid_text($_POST['username']??'',80),valid_text($_POST['password']??'',200));return;}
 if($action==='logout'){$_SESSION=[];session_regenerate_id(true);return;}
 tx(function(&$s)use($action){$u=current_user($s);if(!$u)boom('Bitte anmelden.',401);$id=$u['id'];
  if($action==='password'){$old=valid_text($_POST['old']??'',200);$new=valid_text($_POST['new']??'',200);if(!password_verify($old,$u['hash']))boom('Aktuelles Passwort nicht korrekt.');strong_password($new);if($new!==($_POST['confirm']??''))boom('Passwörter stimmen nicht überein.');if(password_verify($new,$u['hash']))boom('Bitte ein anderes Passwort wählen.');
   $s['users'][$id]['hash']=password_digest($new);$s['users'][$id]['must_change']=false;$s['users'][$id]['version']=bin2hex(random_bytes(12));$_SESSION['version']=$s['users'][$id]['version'];session_regenerate_id(true);audit($s,'Eigenes Passwort geändert',$u);return;}
  if($u['must_change'])boom('Zuerst das Startpasswort ändern.',403);
  version_check($s);
  if($action==='save_menu'){$cat=valid_text($_POST['category']??'',30);if(!array_key_exists($cat,$s['catalog']['menu']))boom('Kategorie unbekannt.');$names=$_POST['name']??[];$descs=$_POST['description']??[];$prices=$_POST['price']??[];$enabled=$_POST['enabled']??[];if(!is_array($names)||count($names)>200)boom('Zu viele Gerichte.');$rows=[];
   foreach($names as$i=>$name){$name=valid_text($name,200);if($name==='')continue;$rows[]=[$name,valid_text($descs[$i]??'',2000),cents($prices[$i]??''),isset($enabled[$i])];}save_snapshot($s);$s['catalog']['menu'][$cat]=$rows;audit($s,'Speisekartenentwurf gespeichert',$u);return;}
  if($action==='save_product'){$p=[];$p['id']=valid_text($_POST['product_id']??'',70);if(!preg_match('/^[a-z0-9][a-z0-9-]{0,69}$/D',$p['id']))boom('Artikel-ID nur Kleinbuchstaben, Zahlen und Bindestriche.');
   foreach(['name'=>200,'brand'=>200,'description'=>2000,'pack'=>80,'note'=>5000,'year'=>20]as$k=>$limit)$p[$k]=valid_text($_POST[$k]??'',$limit);if($p['name']==='')boom('Name fehlt.');
   $p['category']=valid_text($_POST['category']??'',30);if(!in_array($p['category'],['conservas','embutidos','weisswein','rotwein'],true))boom('Kategorie unbekannt.');
   $p['unit']=valid_text($_POST['unit']??'',3);if(!in_array($p['unit'],['g','ml'],true))boom('Einheit fehlt.');$p['amount']=number($_POST['amount']??'',1,50000);$p['price']=cents($_POST['price']??'');$p['case']=number($_POST['case']??'0',0,24);$p['casePrice']=$p['case']?cents($_POST['casePrice']??''):0;
   $p['source']=valid_text($_POST['source']??'',1500);if($p['source']!==''&&(!filter_var($p['source'],FILTER_VALIDATE_URL)||parse_url($p['source'],PHP_URL_SCHEME)!=='https'))boom('Referenz muss eine HTTPS-Adresse sein.');$p['pickup']=isset($_POST['pickup']);$p['active']=isset($_POST['active']);$p['stock']=number($_POST['stock']??'0',0,100000);
   save_snapshot($s);$found=false;foreach($s['catalog']['products']as$i=>$old)if($old['id']===$p['id']){$s['catalog']['products'][$i]=$p;$found=true;break;}if(!$found)$s['catalog']['products'][]=$p;audit($s,'Artikelentwurf gespeichert: '.$p['id'],$u);return;}
  if($action==='user_save'){if($u['role']!=='admin')boom('Nur Administratoren.',403);$target=valid_text($_POST['user_id']??'',80);$existing=$s['users'][$target]??null;$name=valid_text($_POST['user_name']??'',80);if($name==='')boom('Benutzername fehlt.');foreach($s['users']as$other)if($other['id']!==$target&&normalize_username($other['name'])===normalize_username($name))boom('Benutzername bereits vergeben.');
   $role=($_POST['role']??'editor')==='admin'?'admin':'editor';$active=isset($_POST['active']);if($target===$id&&(!$active||$role!=='admin'))boom('Eigenen Administratorzugang hier nicht sperren.');
   if($existing&&$existing['role']==='admin'&&$existing['active']&&(!$active||$role!=='admin')){$others=array_filter($s['users'],fn($x)=>$x['id']!==$target&&$x['active']&&$x['role']==='admin');if(!$others)boom('Mindestens ein Administrator muss aktiv bleiben.');}
   $pass=valid_text($_POST['initial_password']??'',200);if(!$existing||$pass!=='')strong_password($pass);$target=$existing?$target:bin2hex(random_bytes(10));$new=$existing??['id'=>$target,'must_change'=>true];$new['name']=$name;$new['role']=$role;$new['active']=$active;if($pass!==''){$new['hash']=password_digest($pass);$new['must_change']=true;}$new['version']=bin2hex(random_bytes(12));$s['users'][$target]=$new;if($target===$id)$_SESSION['version']=$new['version'];audit($s,'Teamkonto aktualisiert: '.$name,$u);return;}
  if($action==='restore'){$n=number($_POST['snapshot']??'',0,11);if(!isset($s['history'][$n]))boom('Sicherung fehlt.');$restored=$s['history'][$n]['catalog'];save_snapshot($s);$s['catalog']=$restored;audit($s,'Entwurf aus Sicherung wiederhergestellt',$u);return;}
  if($action==='publish'){if($u['role']!=='admin')boom('Nur Administratoren veröffentlichen.',403);$catalog=$s['catalog'];foreach($catalog['menu']as$cat=>$rows){$catalog['menu'][$cat]=array_values(array_map(fn($x)=>array_slice($x,0,3),array_filter($rows,fn($x)=>($x[3]??true))));}$catalog['products']=array_values(array_filter($catalog['products'],fn($p)=>$p['active']??true));
   $data=private_dir().'/publish-'.bin2hex(random_bytes(8)).'.json';file_put_contents($data,json_encode($catalog,JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR));chmod($data,0600);
   $cmd=[getenv('VDE_PYTHON')?:'/usr/bin/python3',PROJECT.'/server/publish.py',$data];$pipes=[];$proc=proc_open($cmd,[0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']],$pipes,PROJECT);if(!is_resource($proc)){unlink($data);boom('Veröffentlichungsdienst fehlt.',503);}fclose($pipes[0]);$log=stream_get_contents($pipes[1]);$err=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);$code=proc_close($proc);unlink($data);if($code!==0){error_log('VDE publish: '.$err);boom('Veröffentlichung fehlgeschlagen. Entwurf bleibt gespeichert.',503);}$s['published_at']=gmdate('c');audit($s,'Restaurant und Shop veröffentlicht',$u);return;}
  boom('Aktion unbekannt.');});
}
