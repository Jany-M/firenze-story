// Record name → page of the reader encyclopedia (/library/<slug>/, built from docs/encyclopedia/*.md).
// Add a line when a landmark gets its library page.
const PAGES: [RegExp, string][] = [
  [/santa maria del fiore|^duomo/i, 'duomo'],
  [/campanile di giotto/i, 'campanile'],
  [/battistero/i, 'baptistery'],
  [/palazzo vecchio|palazzo della signoria/i, 'palazzo-vecchio'],
  [/loggia dei lanzi|loggia della signoria/i, 'loggia-dei-lanzi'],
  [/ponte vecchio/i, 'ponte-vecchio'],
  [/orsanmichele/i, 'orsanmichele'],
  [/bargello|palazzo del podest/i, 'bargello'],
  [/santa croce/i, 'santa-croce'],
  [/santa maria novella/i, 'santa-maria-novella'],
  [/uffizi/i, 'uffizi'],
  [/san lorenzo|cappella dei principi|cappelle medicee|sagrestia (vecchia|nuova)|laurenziana/i, 'san-lorenzo'],
  [/medici riccardi|^palazzo medici$/i, 'medici-riccardi'],
  [/corridoio vasariano|vasari corridor|torre dei mannelli/i, 'vasari-corridor'],
  [/palazzo pitti|meridiana|boboli|buontalenti|kaffeehaus|forte di belvedere/i, 'pitti-boboli'],
  [/palazzo strozzi/i, 'palazzo-strozzi'],
  [/piazza della repubblica|arcone|colonna dell'abbondanza/i, 'piazza-della-repubblica'],
  [/mercato centrale|mercato di san lorenzo/i, 'mercato-centrale'],
  [/annunziata|innocenti|servi di maria|serviti|mostri marini/i, 'santissima-annunziata'],
  [/loggia del pesce|piazza dei ciompi/i, 'loggia-del-pesce'],
  [/santo spirito/i, 'santo-spirito'],
  [/san marco/i, 'san-marco'],
  [/carmine|cappella corsini|brancacci/i, 'carmine'],
  [/santa felicita/i, 'santa-felicita'],
  [/san mini?ato|palazzo dei vescovi/i, 'san-miniato'],
  [/^porta |^torre (della zecca|san niccol|della serpe)|torrino di santa rosa|arco di trionfo|cerchia|baluardo/i, 'walls-and-gates'],
];
export const libraryUrl = (name: string) => {
  const p = name && PAGES.find(([re]) => re.test(name));
  return p ? `/library/${p[1]}/` : '';
};
