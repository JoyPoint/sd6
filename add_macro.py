import argparse
import yaml
from collections import *

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

parser = argparse.ArgumentParser()
parser.add_argument('--type', choices=['attributes', 'library', 'language'], required=True)
parser.add_argument('--name', required=True)
parser.add_argument('--value', required=True, type=int)
parser.add_argument('--papers', nargs='+')
parser.add_argument('--headers', nargs='*')
args = parser.parse_args()

existing = ordered_load(open('macros.yaml'))
yaml.Dumper.ignore_aliases = lambda *args: True

values = [('value', args.value),
          ('papers', ' '.join(args.papers))]
specific = existing[args.type]
for row in specific:
    if row['name'] == args.name:
        for entry in row['rows']:
            if entry['value'] == args.value:
                # just add this paper
                old_papers = entry['papers'].split()
                old_papers.extend(args.papers)
                old_papers.sort()
                entry['papers'] = ' '.join(old_papers)
                break
        else:
            # add a new row
            row['rows'].append(OrderedDict(values))
        break
else:
    # add a new macro
    items = [('name', args.name)]
    if args.type == 'library':
        if not args.headers:
            parser.error('new library macros require headers')
        items.append(('header_list', ' '.join(args.headers)))

    items.append(('rows', [OrderedDict(values)]))
    specific.append(OrderedDict(items))
specific.sort(key=lambda d: d['name'])

# https://stackoverflow.com/a/8661021/2069064
represent_dict_order = lambda self, data:self.represent_mapping('tag:yaml.org,2002:map', data.items())
yaml.add_representer(OrderedDict, represent_dict_order)
yaml.dump(existing, open('macros.yaml', 'w'), default_flow_style=False)
