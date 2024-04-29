function outstring = makecellarraystr(incell)
% Function to take a cell array { 'A', 'B', 'C' } and return that same cell
% array formatted as a string '{ 'A', 'B', 'C' }'.
%
% example: outstring = makecellarraystr({ 'A', 'B', 'C' })

      outstring = sprintf('{');
      for cE = 1:size(incell,2)
          outstring = sprintf('%s ''%s''', outstring, incell{cE});
          if (cE ~= size(incell,2))
              outstring = sprintf('%s,', outstring);
          end
      end
      outstring = sprintf('%s }', outstring);
end