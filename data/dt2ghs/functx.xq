module namespace functx = "http://www.functx.com";

(:http://www.xqueryfunctions.com/xq/functx_substring-before-last.html:)
declare function functx:substring-before-last($arg as xs:string?, $delim as xs:string) as xs:string {
  if (matches($arg, functx:escape-for-regex($delim)))
   then replace($arg, concat('^(.*)', functx:escape-for-regex($delim),'.*'), '$1')
   else ''
 };

(:http://www.xqueryfunctions.com/xq/functx_escape-for-regex.html:)
declare function functx:escape-for-regex($arg as xs:string?) as xs:string {
  replace($arg, '(\.|\[|\]|\\|\||\-|\^|\$|\?|\*|\+|\{|\}|\(|\))','\\$1')
 };

(:http://www.xqueryfunctions.com/xq/functx_trim.html:)
declare function functx:trim ($arg as xs:string?) as xs:string {
  replace(replace($arg,'\s+$',''),'^\s+','')
};


(: ======================================:)
(: INUTILE EN L’ÉTAT. GARDER ? :)

(:http://www.xqueryfunctions.com/xq/functx_capitalize-first.html:)
declare function functx:capitalize-first($arg as xs:string?) as xs:string? {
  concat(upper-case(substring($arg,1,1)), substring($arg,2))
 };

(:http://www.xqueryfunctions.com/xq/functx_is-a-number.html:)
declare function functx:is-a-number($value as xs:anyAtomicType?) as xs:boolean {
  string(number($value)) != 'NaN'
 };

(:http://www.xqueryfunctions.com/xq/functx_replace-first.html:)
declare function functx:replace-first ($arg as xs:string?, $pattern as xs:string , $replacement as xs:string ) as xs:string {
  replace($arg, concat('(^.*?)', $pattern),
  concat('$1',$replacement))
};

(:http://www.xqueryfunctions.com/xq/functx_index-of-match-first.html:)
declare function functx:index-of-match-first ($arg as xs:string?, $pattern as xs:string) as xs:integer? {
  if (matches($arg,$pattern))
    then string-length(tokenize($arg, $pattern)[1]) + 1
  else ()
};

(:http://www.xqueryfunctions.com/xq/functx_get-matches-and-non-matches.html:)
declare function functx:get-matches-and-non-matches ($string as xs:string?, $regex as xs:string) as element()* {
  let $iomf := functx:index-of-match-first($string, $regex)
  return
    if (empty($iomf))
      then <non-match>{$string}</non-match>
    else if ($iomf > 1)
      then (<non-match>{substring($string,1,$iomf - 1)}</non-match>, functx:get-matches-and-non-matches(substring($string,$iomf),$regex))
    else
      let $length := string-length($string) - string-length(functx:replace-first($string, $regex,''))
  return (<match>{substring($string,1,$length)}</match>,
    if (string-length($string) > $length)
      then functx:get-matches-and-non-matches(substring($string,$length + 1),$regex)
    else ()
  )
};

(:http://www.xqueryfunctions.com/xq/functx_get-matches.html:)
declare function functx:get-matches ($string as xs:string?, $regex as xs:string) as xs:string* {
  functx:get-matches-and-non-matches($string,$regex)/string(self::match)
};
